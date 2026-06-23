# ============================================================
# aws-stop.ps1 - Para todos los recursos AWS para ahorrar costes
#
# Qué hace:
#   1. Escala ECS services a 0 tareas
#   2. Para la instancia RDS
#   3. Elimina el NAT Gateway (mayor ahorro: ~$32/mes)
#   4. Libera la Elastic IP asociada (si no fue auto-liberada)
#
# Uso: .\phishing-detect\scripts\aws-stop.ps1
# ============================================================

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Continue"

# ---- CONFIGURACION ----
$REGION   = "eu-north-1"
$CLUSTER  = "phishing-detect"
$SERVICES = @("svc-app", "svc-worker", "svc-qdrant")
$DB_ID    = "phishing-detect-db"
$VPC_CIDR = "10.0.0.0/16"
# -----------------------

function Write-Step($msg) { Write-Host "`n>>> $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "    OK: $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "    WARN: $msg" -ForegroundColor Yellow }
function Write-Fail($msg) { Write-Host "    ERROR: $msg" -ForegroundColor Red }

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

Write-Host "`n===== PARAR INFRAESTRUCTURA AWS - phishing-detect =====" -ForegroundColor Magenta
Write-Host "Region: $REGION  |  Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"

# ---- 1. Escalar ECS a 0 ----
Write-Step "Escalando servicios ECS a 0..."
foreach ($svc in $SERVICES) {
    Write-Host "    Parando $svc..."
    try {
        Invoke-AWS { aws ecs update-service --cluster $CLUSTER --service $svc --desired-count 0 --region $REGION --output text --query "service.serviceName" } | Out-Null
        Write-OK "$svc -> desired=0"
    } catch {
        Write-Fail "No se pudo parar ${svc}: $_"
    }
}

# ---- 2. Parar RDS ----
Write-Step "Parando RDS ($DB_ID)..."
try {
    $rdsStatus = Invoke-AWS { aws rds describe-db-instances --db-instance-identifier $DB_ID --region $REGION --query "DBInstances[0].DBInstanceStatus" --output text }
    $rdsStatus = $rdsStatus.Trim()

    if ($rdsStatus -eq "available") {
        Invoke-AWS { aws rds stop-db-instance --db-instance-identifier $DB_ID --region $REGION --output text --query "DBInstance.DBInstanceStatus" } | Out-Null
        Write-OK "RDS enviado a stop (tarda ~2 min)"
    } elseif ($rdsStatus -eq "stopped") {
        Write-Warn "RDS ya estaba parado"
    } else {
        Write-Warn "RDS en estado '$rdsStatus', no se puede parar ahora"
    }
} catch {
    Write-Fail "Error con RDS: $_"
}

# ---- 3. Eliminar NAT Gateway ----
Write-Step "Buscando NAT Gateway en VPC (CIDR $VPC_CIDR)..."
try {
    $VPC_ID = (Invoke-AWS { aws ec2 describe-vpcs --filters "Name=cidr-block,Values=$VPC_CIDR" --region $REGION --query "Vpcs[0].VpcId" --output text }).Trim()

    if ($VPC_ID -eq "None" -or $VPC_ID -eq "") {
        Write-Warn "No se encontro la VPC con CIDR $VPC_CIDR"
    } else {
        Write-Host "    VPC ID: $VPC_ID"

        $NAT_JSON = Invoke-AWS { aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=$VPC_ID" "Name=state,Values=available,pending" --region $REGION --query "NatGateways[*].{ID:NatGatewayId,EIP:NatGatewayAddresses[0].AllocationId}" --output json }
        $NAT_INFO = $NAT_JSON | ConvertFrom-Json

        if ($NAT_INFO.Count -eq 0) {
            Write-Warn "No hay NAT Gateways activos en la VPC (ya eliminado o no existe)"
        } else {
            foreach ($nat in $NAT_INFO) {
                $NAT_ID   = $nat.ID
                $ALLOC_ID = $nat.EIP
                Write-Host "    NAT Gateway: $NAT_ID  (EIP: $ALLOC_ID)"

                Invoke-AWS { aws ec2 delete-nat-gateway --nat-gateway-id $NAT_ID --region $REGION --output text --query "NatGatewayId" } | Out-Null
                Write-OK "NAT Gateway $NAT_ID - eliminacion iniciada"

                # Esperar hasta deleted para poder liberar la EIP
                if ($ALLOC_ID -and $ALLOC_ID -ne "None") {
                    Write-Host "    Esperando confirmacion de eliminacion..."
                    $maxWait = 120
                    $elapsed = 0
                    do {
                        Start-Sleep -Seconds 10
                        $elapsed += 10
                        $state = (Invoke-AWS { aws ec2 describe-nat-gateways --nat-gateway-ids $NAT_ID --region $REGION --query "NatGateways[0].State" --output text }).Trim()
                        Write-Host "    Estado NAT: $state ($elapsed s)"
                    } while ($state -ne "deleted" -and $elapsed -lt $maxWait)

                    if ($state -eq "deleted") {
                        try {
                            Invoke-AWS { aws ec2 release-address --allocation-id $ALLOC_ID --region $REGION }
                            Write-OK "Elastic IP $ALLOC_ID liberada"
                        } catch {
                            # AWS libera la EIP automaticamente en algunos casos
                            Write-Warn "EIP no encontrada (probablemente liberada automaticamente por AWS)"
                        }
                    } else {
                        Write-Warn "NAT no llego a 'deleted' en ${maxWait}s. Libera la EIP manualmente si sigue asignada."
                    }
                }
            }
        }
    }
} catch {
    Write-Fail "Error buscando/eliminando NAT Gateway: $_"
}

# ---- Resumen ----
Write-Host "`n===== RESUMEN =====" -ForegroundColor Magenta
Write-Host "ECS services  -> desired=0 (sin coste)"
Write-Host "RDS           -> parado (solo storage: ~`$0.10/mes)"
Write-Host "NAT Gateway   -> eliminado (ahorro ~`$32/mes)"
Write-Host ""
Write-Host "Siguen corriendo (sin opcion stop):"
Write-Host "  ElastiCache  ~`$12/mes"
Write-Host "  ALB          ~`$5/mes"
Write-Host ""
Write-Host "Para levantar: .\phishing-detect\scripts\aws-start.ps1" -ForegroundColor Yellow
