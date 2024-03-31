def create_survey_auth_link(user, redirect_link_patterns, survey):
    return redirect_link_patterns.format(survey)


def create_auth_claim(user, email_token, **kwargs):
    return {"email": user.email, "token": email_token.key, "survey": kwargs["survey"]}
