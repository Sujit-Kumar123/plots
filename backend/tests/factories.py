import uuid

import factory


class UserFactory(factory.Factory):
    class Meta:
        model = dict

    email = factory.LazyFunction(lambda: f"user-{uuid.uuid4().hex[:8]}@example.com")
    password = "TestPass123!"
    fname = factory.Faker("first_name")
    lname = factory.Faker("last_name")


class AdminFactory(UserFactory):
    pass
