from users.models import CustomUser

def create_remaining_users(target_total=3905):
    existing_users = CustomUser.objects.filter(is_superuser=False).count()
    users_to_create = target_total - existing_users

    print(f"Existing users: {existing_users}")
    print(f"Users to create: {users_to_create}")

    if users_to_create <= 0:
        print("✅ You already have enough users.")
        return

    for i in range(existing_users + 1, target_total + 1):
        email = f"user{i}@example.com"
        first = f"User{i}"
        last = "Tree"
        CustomUser.objects.create_user(
            email=email,
            first_name=first,
            last_name=last,
            password="testpass123"
        )
        if i % 100 == 0:
            print(f"Created {i} users...")

    print("✅ All users created.")
