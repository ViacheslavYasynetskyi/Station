from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from station.models import Bus, Trip, Facility, Ticket, Order


class FacilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Facility
        fields = ("id", "name",)


class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ["id", "info", "num_seats", "is_mini", "facilities"]


class BusListSerializer(BusSerializer):
    facilities = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")


class BusDetailSerializer(BusSerializer):
    facilities = FacilitySerializer(many=True, read_only=True)


class BusImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bus
        fields = ("id", "image")

# class BusSerializer(serializers.Serializer):
    # id = serializers.IntegerField(read_only=True)
    # info = serializers.CharField(required=False)
    # num_seats = serializers.IntegerField(required=True)
    #
    # def create(self, validated_data):
    #     return Bus.objects.create(**validated_data)
    #
    # def update(self, instance, validated_data):
    #     instance.info = validated_data.get("info", instance.info)
    #     instance.num_seats = validated_data.get("num_seats", instance.num_seats)
    #     instance.save()
    #     return instance


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_seat(attrs["seat"], attrs["trip"].bus.num_seats, serializers.ValidationError)

        return data

    class Meta:
        model = Ticket
        fields = ("id", "seat", "trip")
        validators = [
            UniqueTogetherValidator(
                queryset=Ticket.objects.all(), fields=["seat", "trip"]
            )
        ]


class TripSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trip
        fields = ("id", "source", "destination", "departure", "bus")


class TripListSerializer(TripSerializer):
    bus_info = serializers.CharField(source="bus.info", read_only=True)
    bus_num_seats = serializers.IntegerField(source="bus.num_seats", read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Trip
        fields = (
            "id",
            "source",
            "destination",
            "departure",
            "bus_info",
            "bus_num_seats",
            "tickets_available",
        )


class TripDetailSerializer(TripSerializer):
    bus = BusDetailSerializer(many=False, read_only=True)
    taken_seats = serializers.SlugRelatedField(
        source="tickets",
        many=True,
        read_only=True,
        slug_field="seat"
    )

    class Meta:
        model = Trip
        fields = ("id", "source", "destination", "departure", "bus", "taken_seats")


class TicketListSerializer(TicketSerializer):
    trip = TripListSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
