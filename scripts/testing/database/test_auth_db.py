#!/usr/bin/env python3
"""Test database authentication system"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.services.auth_service import auth_service


async def test_auth_system():
    """Test the database-backed authentication system"""

    print("🏛️ Cidadão.AI - Testing Database Authentication\n")

    # Test user credentials
    test_email = "test@cidadao.ai"
    test_password = "TestPassword123!"
    test_username = "testuser"
    test_name = "Test User"

    try:
        # 1. Create a test user
        print("1. Creating test user...")
        user = await auth_service.create_user(
            username=test_username,
            email=test_email,
            password=test_password,
            full_name=test_name,
        )
        print(f"✅ User created: {user['email']}")

        # 2. Authenticate user
        print("\n2. Testing authentication...")
        authenticated = await auth_service.authenticate_user(test_email, test_password)
        if authenticated:
            print(f"✅ Authentication successful for: {authenticated['email']}")
        else:
            print("❌ Authentication failed")

        # 3. Create tokens
        print("\n3. Creating JWT tokens...")
        access_token = auth_service.create_access_token({"sub": str(user["id"])})
        refresh_token = auth_service.create_refresh_token({"sub": str(user["id"])})
        print(f"✅ Access token created (length: {len(access_token)})")
        print(f"✅ Refresh token created (length: {len(refresh_token)})")

        # 4. Verify token
        print("\n4. Verifying access token...")
        payload = await auth_service.verify_token(access_token)
        print(f"✅ Token verified, user_id: {payload.get('sub')}")

        # 5. Get current user from token
        print("\n5. Getting user from token...")
        current_user = await auth_service.get_current_user(access_token)
        if current_user:
            print(f"✅ Current user: {current_user['email']}")

        # 6. Test refresh token
        print("\n6. Testing token refresh...")
        new_tokens = await auth_service.refresh_access_token(refresh_token)
        print(
            f"✅ New access token created (length: {len(new_tokens['access_token'])})"
        )

        # 7. Test password change
        print("\n7. Testing password change...")
        new_password = "NewPassword456!"
        success = await auth_service.change_password(
            user_id=user["id"],
            current_password=test_password,
            new_password=new_password,
        )
        if success:
            print("✅ Password changed successfully")

            # Verify new password works
            auth_check = await auth_service.authenticate_user(test_email, new_password)
            if auth_check:
                print("✅ New password verified")

        # 8. Test token blacklist
        print("\n8. Testing token revocation...")
        await auth_service.revoke_token(access_token, "Testing revocation")
        try:
            await auth_service.verify_token(access_token)
            print("❌ Token should have been revoked!")
        except Exception:
            print("✅ Token successfully revoked")

        # 9. Test with wrong password
        print("\n9. Testing failed authentication...")
        failed_auth = await auth_service.authenticate_user(test_email, "wrong_password")
        if not failed_auth:
            print("✅ Failed authentication handled correctly")

        # 10. Test admin user (from seed data)
        print("\n10. Testing admin user...")
        admin_auth = await auth_service.authenticate_user("admin", "Admin123!")
        if admin_auth:
            print("✅ Admin user authenticated")
        else:
            print("⚠️ Admin user not found (may need to run seed script)")

        print("\n✅ All authentication tests passed!")

    except Exception as e:
        print(f"\n❌ Error during testing: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_auth_system())
