from rest_framework import serializers
from .models import User, Transaction, Expense, Income


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2',
                  'first_name', 'last_name', ]
        extra_kwargs = {
            'password': {'error_messages': {'blank': "Password field cannot be blank."}},
            'password2': {'error_messages': {'blank': "Password field cannot be blank."}},
        }

    def create(self, validated_data):
        import random
        username = f"{validated_data['first_name']}#{random.randint(100000, 999999)}"
        while User.objects.filter(username=username).exists():
            username = f"{self.first_name}#{random.randint(100000, 999999)}"
        user = User(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            username=username
        )
        password = validated_data['password']
        password2 = validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({
                'password': "Password didn't matched"
            })

        user.set_password(password)
        user.save()
        return user


class TransactionSerializer(serializers.ModelSerializer):
    to_transaction_with = serializers.CharField(max_length=20, required=True)

    class Meta:
        model = Transaction
        fields = ['transaction_type',
                  'transaction_detail',
                  'amount', 'to_transaction_with']

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def create(self, validated_data):
        tt = validated_data['transaction_type']
        if (tt == 'C'):
            liney = validated_data['user']
            diney = User.objects.get(
                username=validated_data['to_transaction_with'])
        elif (tt == 'D'):
            diney = validated_data['user']
            liney = User.objects.get(
                username=validated_data['to_transaction_with'])
        t = Transaction(
            transaction_type=tt,
            liney=liney,
            diney=diney,
            added_by=validated_data['user'],
            transaction_detail=validated_data['transaction_detail'],
            amount=validated_data['amount'],
        )
        to_transaction_with_user = User.objects.get(
            username=validated_data['to_transaction_with'])
        t.to_be_verified_by = to_transaction_with_user
        t.save()
        return t


class TransactionSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'type', 'amount', 'category',
                  'description', 'created_at']

    def create(self, validated_data):
        expense = Expense(amount=validated_data['amount'], user=validated_data['user'],
                          description=validated_data['description'], category=validated_data['category'])
        expense.save()
        return expense

    def update(self, instance, validated_data):
        instance.category = validated_data.get('category', instance.category)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.save()
        return instance


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ['id', 'type', 'amount',
                  'category', 'description', 'created_at']

    def create(self, validated_data):
        income = Income(amount=validated_data['amount'], user=validated_data['user'],
                        description=validated_data['description'], category=validated_data['category'])
        income.save()
        return income

    def update(self, instance, validated_data):
        instance.category = validated_data.get('category', instance.category)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.save()
        return instance
