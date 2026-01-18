#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "y", "on")


def _should_ensure_superuser(argv: list[str]) -> bool:
    # Only run this on `runserver` to avoid side effects for other commands.
    if len(argv) < 2 or argv[1] != "runserver":
        return False
    # On by default for local/dev runs; opt-out via env.
    return _env_bool("SCALEREG_CREATE_SUPERUSER", True)


def _ensure_default_superuser() -> None:
    if not _should_ensure_superuser(sys.argv):
        return

    # Prefer SCALEREG_* vars, but accept Django's conventional vars too.
    username = (
        os.environ.get("SCALEREG_SUPERUSER_USERNAME")
        or os.environ.get("DJANGO_SUPERUSER_USERNAME")
        or "admin"
    )
    email = (
        os.environ.get("SCALEREG_SUPERUSER_EMAIL")
        or os.environ.get("DJANGO_SUPERUSER_EMAIL")
        or "admin@example.com"
    )
    explicit_password = (
        os.environ.get("SCALEREG_SUPERUSER_PASSWORD")
        or os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    )
    password = explicit_password or "admin"
    reset_existing_password = explicit_password is not None or _env_bool(
        "SCALEREG_RESET_SUPERUSER_PASSWORD", False
    )

    try:
        import django
        from django.contrib.auth import get_user_model
        from django.db.utils import OperationalError, ProgrammingError
    except Exception:
        return

    try:
        django.setup()
        User = get_user_model()
        username_field = getattr(User, "USERNAME_FIELD", "username")

        lookup = {username_field: username}
        user = User.objects.filter(**lookup).first()
        if user is None:
            create_kwargs = {username_field: username}
            if email and "email" in {f.name for f in User._meta.fields}:
                create_kwargs["email"] = email
            user = User.objects.create_superuser(**create_kwargs)
            if password:
                user.set_password(password)
            user.save()
            return

        changed = False
        if not getattr(user, "is_superuser", False):
            user.is_superuser = True
            changed = True
        if not getattr(user, "is_staff", False):
            user.is_staff = True
            changed = True
        if hasattr(user, "email") and email and user.email != email:
            user.email = email
            changed = True
        if reset_existing_password and password:
            user.set_password(password)
            changed = True
        if changed:
            user.save()
    except (OperationalError, ProgrammingError):
        # Usually indicates migrations haven't run yet.
        return


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scalereg3.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    _ensure_default_superuser()
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
