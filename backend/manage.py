#!/usr/bin/env python
"""CLI management commands for Budget Tracker."""

import argparse
import asyncio
import getpass
import sys


async def create_local_user(email: str, display_name: str, password: str) -> None:
    import bcrypt

    from app.config import get_settings
    from app.db.session import AsyncSessionLocal
    from app.repositories.user import LocalUserRepository, UserRepository

    settings = get_settings()
    if not settings.local_auth_enabled:
        print("ERROR: LOCAL_AUTH_ENABLED is not set to true", file=sys.stderr)
        sys.exit(1)

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        local_repo = LocalUserRepository(session)

        # Check if user already exists
        existing = await user_repo.get_by_email(email)
        if existing:
            # Check if local_user already created
            from app.repositories.user import LocalUserRepository
            existing_local = await local_repo.get_by_email(email)
            if existing_local:
                print(f"ERROR: Local user with email '{email}' already exists", file=sys.stderr)
                sys.exit(1)
            # Create local_user record for existing user
            await local_repo.create(
                user_id=existing.id,
                email=email,
                password_hash=password_hash,
            )
            await session.commit()
            print(f"Local credentials created for existing user: {email}")
            return

        # Create user + local_user
        from app.config import get_settings as gs
        s = gs()
        user = await user_repo.create(
            sub=f"local:{email}",
            email=email,
            display_name=display_name,
            base_currency=s.base_currency,
            auth_provider="local",
        )
        await local_repo.create(
            user_id=user.id,
            email=email,
            password_hash=password_hash,
        )
        await session.commit()
        print(f"Local user created: {email} (id={user.id})")


async def reset_local_password(email: str, new_password: str) -> None:
    import bcrypt

    from app.config import get_settings
    from app.db.session import AsyncSessionLocal
    from app.repositories.user import LocalUserRepository

    settings = get_settings()
    if not settings.local_auth_enabled:
        print("ERROR: LOCAL_AUTH_ENABLED is not set to true", file=sys.stderr)
        sys.exit(1)

    password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

    async with AsyncSessionLocal() as session:
        repo = LocalUserRepository(session)
        local_user = await repo.get_by_email(email)
        if not local_user:
            print(f"ERROR: No local user with email '{email}'", file=sys.stderr)
            sys.exit(1)

        await repo.update(local_user, password_hash=password_hash)
        await session.commit()
        print(f"Password reset for: {email}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Budget Tracker management CLI")
    subparsers = parser.add_subparsers(dest="command")

    # create-local-user
    create_parser = subparsers.add_parser("create-local-user", help="Create a local auth user")
    create_parser.add_argument("--email", required=True, help="User email")
    create_parser.add_argument("--name", required=True, dest="display_name", help="Display name")
    create_parser.add_argument(
        "--password", help="Password (will prompt if not provided)"
    )

    # reset-local-password
    reset_parser = subparsers.add_parser("reset-local-password", help="Reset a local user password")
    reset_parser.add_argument("--email", required=True, help="User email")
    reset_parser.add_argument(
        "--password", help="New password (will prompt if not provided)"
    )

    args = parser.parse_args()

    if args.command == "create-local-user":
        password = args.password or getpass.getpass("Password: ")
        asyncio.run(create_local_user(args.email, args.display_name, password))

    elif args.command == "reset-local-password":
        password = args.password or getpass.getpass("New password: ")
        asyncio.run(reset_local_password(args.email, password))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
