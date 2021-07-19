from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, validators, RadioField, SubmitField


class ProfileUpdateForm(FlaskForm):
    first_name = StringField("First name")
    last_name = StringField("Last name")

    language = SelectField(
        "언어",
        choices=[
            ("", "미입력"),
            ("ko", "한글"),
            ("en", "영어"),
        ],
        validators=[validators.DataRequired("언어 설정은 필수 입력입니다.")],
    )
    country = SelectField(
        "국가",
        choices=[
            ("", "미입력"),
            ("kr", "한국"),
            ("us", "미국"),
            ("vn", "베트남"),
        ],
        validators=[validators.DataRequired("국가 설정은 필수 입력입니다.")],
    )
    gender = RadioField(
        "성별",
        choices=[("M", "남성"), ("F", "여성"), ("U", "공개 안함")],
        validators=[validators.DataRequired("성별 설정은 필수 입력입니다.")],
    )

    submit = SubmitField("Save")

    def validate(self):
        # remove certain form fields depending on user manager config
        # user_manager =  current_app.user_manager
        # if not user_manager.USER_ENABLE_USERNAME:
        #     delattr(self, 'username')
        # if not user_manager.USER_ENABLE_EMAIL:
        #     delattr(self, 'email')
        # if not user_manager.USER_REQUIRE_RETYPE_PASSWORD:
        #     delattr(self, 'retype_password')
        # if not super(ProfileUpdateForm, self).validate():
        #     return False
        # All is well
        return True
