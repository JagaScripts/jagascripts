import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoanComponent } from './component/loan/loan.component';
import { SidebarComponent } from './component/sidebar/sidebar.component';
import { NavbarComponent } from './component/navbar/navbar.component';
import { SignupComponent } from './component/signup/signup.component';
import { SigninComponent } from './component/signin/signin.component';
import { BookdetailsComponent } from './component/bookdetails/bookdetails.component';
import { HomeComponent } from './component/home/home.component';
import { ValueComponent } from './component/value/value.component';
import { ProfileuserComponent } from './component/profileuser/profileuser.component';
import { ProfileadminComponent } from './component/profileadmin/profileadmin.component';
import { FooterComponent } from './component/footer/footer.component';
import { ExchangeComponent } from './component/exchange/exchange.component';
import { BookcommentComponent } from './component/bookcomment/bookcomment.component';

@NgModule({
  declarations: [
    AppComponent,
    LoanComponent,
    SidebarComponent,
    NavbarComponent,
    SignupComponent,
    SigninComponent,
    BookdetailsComponent,
    HomeComponent,
    ValueComponent,
    ProfileuserComponent,
    ProfileadminComponent,
    FooterComponent,
    ExchangeComponent,
    BookcommentComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
