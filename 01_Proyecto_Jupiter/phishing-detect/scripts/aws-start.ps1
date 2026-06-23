# ============================================================
# aws-start.ps1 - Levanta todos los recursos AWS
#
# Qué hace:
#   1. Crea un nuevo NAT Gateway en la subnet publica 1a
#   2. Actualiza la route table de subnets privadas
#   3. Arranca RDS y espera que este disponible (~3-5 min)
#   4. Escala ECS services a 1 (qdrant primero, luego app y worker)
#
# Uso: .\phishing-detect\scripts\aws-start.ps1
# ============================================================

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Continue"

# ---- CONFIGURACION ----
$REGION              = "eu-north-1"
$CLUSTER             = "phishing-detect"
$SERVICES            = @("svc-qdrant", "svc-app", "svc-worker")   # qdrant primero
$DB_ID               = "phishing-detect-db"
$VPC_CIDR            = "10.0.0.0/16"
$PUBLIC_SUBNET_CIDR  = "10.0.0.0/20"     # subnet publica 1a (eu-north-1a)
$PRIVATE_SUBNET_CIDR = "10.0.128.0/20"   # subnet privada 1a (para encontrar su route table)
# -----------------------

function Write-Step($msg) { Write-Host "`n>>> $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "    OK: $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "    WARN: $msg" -ForegroundColor Yellow }

function Invoke-AWS {
    param([scriptblock]$cmd)
    $result = & $cmd 2>&1
    if ($LASTEXITCODE -ne 0) {
        $errMsg = $result | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] } | ForEach-Object { $_.ToString() }
        if (-not $errMsg) { $errMsg = $result -join " " }
        throw $errMsg
    }
    return ($result | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] })
}

Write-Host "`n===== LEVANTAR INFRAESTRUCTURA AWS - phishing-detect =====" -ForegroundColor Magenta
Write-Host "Region: $REGION  |  Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"

# ---- 0. Obtener VPC ID ----
Write-Step "Obteniendo VPC (CIDR $VPC_CIDR)..."
$VPC_ID = (Invoke-AWS { aws ec2 describe-vpcs --filters "Name=cidr-block,Values=$VPC_CIDR" --region $REGION --query "Vpcs[0].VpcId" --output text }).Trim()

if ($VPC_ID -eq "None" -or $VPC_ID -eq "") {
    Write-Host "ERROR: No se encontro la VPC con CIDR $VPC_CIDR" -ForegroundColor Red
    exit 1
}
Write-OK "VPC ID: $VPC_ID"

# ---- 1. Crear NAT Gateway (si no existe) ----
Write-Step "Verificando NAT Gateway..."

$EXISTING_NAT = (Invoke-AWS { aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=$VPC_ID" "Name=state,Values=available,pending" --region $REGION --query "NatGateways[0].NatGatewayId" --output text }).Trim()

if ($EXISTING_NAT -ne "None" -and $EXISTING_NAT -ne "") {
    Write-Warn "NAT Gateway ya existe: $EXISTING_NAT"
    $NAT_ID = $EXISTING_NAT
} else {
    # Obtener subnet publica por CIDR
    $PUBLIC_SUBNET_ID = (Invoke-AWS { aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=cidrBlock,Values=$PUBLIC_SUBNET_CIDR" --region $REGION --query "Subnets[0].SubnetId" --output text }).Trim()

    if ($PUBLIC_SUBNET_ID -eq "None" -or $PUBLIC_SUBNET_ID -eq "") {
        Write-Host "ERROR: No se encontro la subnet publica con CIDR $PUBLIC_SUBNET_CIDR" -ForegroundColor Red
        exit 1
    }
    Write-Host "    Subnet publica: $PUBLIC_SUBNET_ID"

    # Asignar nueva Elastic IP
    Write-Host "    Asignando Elastic IP..."
    $ALLOC_ID = (Invoke-AWS { aws ec2 allocate-address --domain vpc --region $REGION --query "AllocationId" --output text }).Trim()
    Write-OK "Elastic IP: $ALLOC_ID"

    # Crear NAT Gateway
    Write-Host "    Creando NAT Gateway..."
    $NAT_ID = (Invoke-AWS { aws ec2 create-nat-gateway --subnet-id $PUBLIC_SUBNET_ID --allocation-id $ALLOC_ID --region $REGION --tag-specifications "ResourceType=natgateway,Tags=[{Key=Name,Value=phishing-detect-nat}]" --query "NatGateway.NatGatewayId" --output text }).Trim()
    Write-OK "NAT Gateway creado: $NAT_ID"

    # Esperar disponibilidad
    Write-Host "    Esperando que el NAT Gateway este disponible (1-2 min)..."
    $maxWait = 180
    $elapsed = 0
    do {
        Start-Sleep -Seconds 15
        $elapsed += 15
        $state = (Invoke-AWS { aws ec2 describe-nat-gateways --nat-gateway-ids $NAT_ID --region $REGION --query "NatGateways[0].State" --output text }).Trim()
        Write-Host "    Estado: $state ($elapsed s)"
    } while ($state -ne "available" -and $elapsed -lt $maxWait)

    if ($state -ne "available") {
        Write-Host "ERROR: NAT Gateway no llego a 'available' en ${maxWait}s" -ForegroundColor Red
        exit 1
    }
    Write-OK "NAT Gateway disponible: $NAT_ID"

    # ---- 2. Actualizar Route Table privada ----
    Write-Step "Actualizando route table de subnets privadas..."

    # Obtener route table de la subnet privada 1a
    $PRIVATE_SUBNET_ID = (Invoke-AWS { aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=cidrBlock,Values=$PRIVATE_SUBNET_CIDR" --region $REGION --query "Subnets[0].SubnetId" --output text }).Trim()

    $RT_ID = (Invoke-AWS { aws ec2 describe-route-tables --filters "Name=association.subnet-id,Values=$PRIVATE_SUBNET_ID" --region $REGION --query "RouteTables[0].RouteTableId" --output text }).Trim()

    if ($RT_ID -eq "None" -or $RT_ID -eq "") {
        Write-Warn "No se encontro route table explicita, usando la main de la VPC"
        $RT_ID = (Invoke-AWS { aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPC_ID" "Name=association.main,Values=true" --region $REGION --query "RouteTables[0].RouteTableId" --output text }).Trim()
    }
    Write-Host "    Route Table: $RT_ID"

    # Comprobar si existe ruta 0.0.0.0/0 (puede estar en blackhole tras borrar el NAT)
    $existingRoute = (Invoke-AWS { aws ec2 describe-route-tables --route-table-ids $RT_ID --region $REGION --query "RouteTables[0].Routes[?DestinationCidrBlock=='0.0.0.0/0'].State" --output text }).Trim()

    if ($existingRoute -ne "None" -and $existingRoute -ne "") {
        # Reemplazar ruta existente (puede estar en blackhole)
        Invoke-AWS { aws ec2 replace-route --route-table-id $RT_ID --destination-cidr-block "0.0.0.0/0" --nat-gateway-id $NAT_ID --region $REGION } | Out-Null
        Write-OK "Ruta 0.0.0.0/0 actualizada -> $NAT_ID"
    } else {
        # Crear nueva ruta
        Invoke-AWS { aws ec2 create-route --route-table-id $RT_ID --destination-cidr-block "0.0.0.0/0" --nat-gateway-id $NAT_ID --region $REGION } | Out-Null
        Write-OK "Ruta 0.0.0.0/0 creada -> $NAT_ID"
    }
}

# ---- 3. Arrancar RDS ----
Write-Step "Arrancando RDS ($DB_ID)..."
try {
    $rdsStatus = (Invoke-AWS { aws rds describe-db-instances --db-instance-identifier $DB_ID --region $REGION --query "DBInstances[0].DBInstanceStatus" --output text }).Trim()

    if ($rdsStatus -eq "available") {
        Write-Warn "RDS ya estaba disponible"
    } elseif ($rdsStatus -eq "stopped") {
        Invoke-AWS { aws rds start-db-instance --db-instance-identifier $DB_ID --region $REGION --output text --query "DBInstance.DBInstanceStatus" } | Out-Null
        Write-OK "RDS iniciando..."

        Write-Host "    Esperando que RDS este disponible (3-5 min)..."
        $maxWait = 360
        $elapsed = 0
        do {
            Start-Sleep -Seconds 20
            $elapsed += 20
            $rdsStatus = (Invoke-AWS { aws rds describe-db-instances --db-instance-identifier $DB_ID --region $REGION --query "DBInstances[0].DBInstanceStatus" --output text }).Trim()
            Write-Host "    Estado RDS: $rdsStatus ($elapsed s)"
        } while ($rdsStatus -ne "available" -and $elapsed -lt $maxWait)

        if ($rdsStatus -eq "available") {
            Write-OK "RDS disponible"
        } else {
            Write-Warn "RDS no llego a 'available' en ${maxWait}s. Los ECS services arrancaran igualmente."
        }
    } else {
        Write-Warn "RDS en estado '$rdsStatus'"
    }
} catch {
    Write-Warn "Error con RDS: $_"
}

# ---- 4. Escalar ECS a 1 ----
Write-Step "Escalando servicios ECS a 1..."
foreach ($svc in $SERVICES) {
    Write-Host "    Levantando $svc..."
    try {
        Invoke-AWS { aws ecs update-service --cluster $CLUSTER --service $svc --desired-count 1 --region $REGION --output text --query "service.serviceName" } | Out-Null
        Write-OK "$svc -> desired=1"
    } catch {
        Write-Host "    ERROR: No se pudo levantar ${svc}: $_" -ForegroundColor Red
    }
}

# ---- Resumen ----
Write-Host "`n===== INFRAESTRUCTURA LEVANTADA =====" -ForegroundColor Magenta
Write-Host "NAT Gateway   -> $NAT_ID"
Write-Host "RDS           -> disponible"
Write-Host "ECS Services  -> desired=1 (qdrant, app, worker)"
Write-Host ""
Write-Host "Los contenedores ECS tardan ~2-3 min en estar listos." -ForegroundColor Yellow
Write-Host ""
Write-Host "Verificar estado ECS:"
Write-Host "  aws ecs describe-services --cluster $CLUSTER --services svc-app svc-worker svc-qdrant --region $REGION --query 'services[*].{name:serviceName,running:runningCount,desired:desiredCount}' --output table"
