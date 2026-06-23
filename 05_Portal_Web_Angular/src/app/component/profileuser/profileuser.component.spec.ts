import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProfileuserComponent } from './profileuser.component';

describe('ProfileuserComponent', () => {
  let component: ProfileuserComponent;
  let fixture: ComponentFixture<ProfileuserComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ProfileuserComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ProfileuserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
