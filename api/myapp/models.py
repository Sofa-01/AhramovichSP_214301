from django.db import models


class Tour(models.Model):
    name = models.CharField(max_length=150)
    places = models.ManyToManyField('Place', 'tours')
    hotels = models.ManyToManyField('Hotel', 'tours')


class Place(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField()
    city = models.ForeignKey('City', models.CASCADE, 'places')


class Hotel(models.Model):
    name = models.CharField(max_length=150)
    stars_count = models.PositiveSmallIntegerField()
    image = models.ImageField()
    city = models.ForeignKey('City', models.CASCADE, 'hotels')

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(stars_count__gte=1, stars_count__lte=5), name='correct_stars_count')
        ]


class TransportType(models.Model):
    name = models.CharField(max_length=75)


class TransportPlace(models.Model):
    city = models.ForeignKey('city', models.CASCADE, 'transport_places')
    name = models.CharField(max_length=150)


class TransportRoute(models.Model):
    name = models.CharField(max_length=75)
    departure = models.ForeignKey('TransportPlace', models.CASCADE, 'departures')
    arrival = models.ForeignKey('TransportPlace', models.CASCADE, 'arrivals')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    places_count = models.PositiveSmallIntegerField()


class City(models.Model):
    name = models.CharField(max_length=75)


class PersonalData(models.Model):
    image = models.ImageField()
    name = models.CharField(max_length=75)
    surname = models.CharField(max_length=75)
    lastname = models.CharField(max_length=75)
    mail = models.CharField(max_length=100)

class FavoriteRoute(models.Model):
    name = models.CharField(max_length=75)
    departure = models.ForeignKey('TransportPlace', models.CASCADE, 'favorite_departures')
    arrival = models.ForeignKey('TransportPlace', models.CASCADE, 'favorite_arrivals')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    places_count = models.PositiveSmallIntegerField()

class Price(models.Model):
    number = models.IntegerField()

