from flask_user import UserManager

try:
    from urllib.parse import quote, unquote  # Python 3
except ImportError:
    from urllib import quote, unquote  # Python 2

from flask import redirect, render_template, request
from flask_login import current_user


class AuthUserManager(UserManager):
    def login_view(self):
        """Prepare and process the login form."""

        # Authenticate username/email and login authenticated users.

        safe_next_url = self._get_safe_next_url("next", self.USER_AFTER_LOGIN_ENDPOINT)
        safe_reg_next = self._get_safe_next_url(
            "reg_next", self.USER_AFTER_REGISTER_ENDPOINT
        )

        # Immediately redirect already logged in users
        if (
            self.call_or_get(current_user.is_authenticated)
            and self.USER_AUTO_LOGIN_AT_LOGIN
        ):
            return redirect(safe_next_url)

        # Initialize form
        login_form = self.LoginFormClass(request.form)  # for login.html
        register_form = self.RegisterFormClass()  # for login_or_register.html
        if request.method != "POST":
            login_form.next.data = register_form.next.data = safe_next_url
            login_form.reg_next.data = register_form.reg_next.data = safe_reg_next

        # Process valid POST
        if request.method == "POST" and login_form.validate():
            # Retrieve User
            user = None
            user_email = None
            if self.USER_ENABLE_USERNAME:
                # Find user record by username
                user = self.db_manager.find_user_by_username(login_form.username.data)

                # Find user record by email (with form.username)
                if not user and self.USER_ENABLE_EMAIL:
                    user, user_email = self.db_manager.get_user_and_user_email_by_email(
                        login_form.username.data
                    )
            else:
                # Find user by email (with form.email)
                user, user_email = self.db_manager.get_user_and_user_email_by_email(
                    login_form.email.data
                )

            if user:
                # Log user in
                safe_next_url = self.make_safe_url(login_form.next.data)
                return self._do_login_user(
                    user, safe_next_url, login_form.remember_me.data
                )

        # Render form
        self.prepare_domain_translations()
        template_filename = (
            self.USER_LOGIN_AUTH0_TEMPLATE
            if self.USER_ENABLE_AUTH0
            else self.USER_LOGIN_TEMPLATE
        )
        return render_template(
            template_filename,
            form=login_form,
            login_form=login_form,
            register_form=register_form,
        )


user_manager = AuthUserManager(None, None, None)
