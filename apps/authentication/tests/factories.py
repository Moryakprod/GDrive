import factory

from ..models import User


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Sequence(lambda n: 'atom{0}@prettyemail.co.uk'.format(n))
    password = factory.PostGenerationMethodCall('set_password', '12345678')
