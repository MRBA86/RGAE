from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, phone_number, email, national_id, password):
        if not phone_number:
            raise ValueError('کاربر باید شماره تلفن داشته باشد')
        if not email:
            raise ValueError('کاربر باید آدرس ایمیل داشته باشد')
        if not national_id:
            raise ValueError('کاربر باید کد ملی داشته باشد')
        
        user = self.model(phone_number=phone_number, email=self.normalize_email(email), national_id=national_id)
        user.set_password(password)
        user.save(using= self._db)
        return user
    
        
    def create_superuser(self, phone_number, email, national_id, password):
        user = self.create_user(phone_number=phone_number, email=email, national_id=national_id, password=password)
        user.is_admin = True
        user.save(using= self._db)
        return user