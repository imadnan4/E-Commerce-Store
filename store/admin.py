from django.contrib import admin
from .models import Category, Product, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'is_available', 'category']
    list_editable = ['price', 'stock', 'is_available']
    prepopulated_fields = {'slug': ('name',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_editable = ['status']
    inlines = [OrderItemInline]from django.contrib import admin
    from .models import Category, Product, Order, OrderItem

    @admin.register(Category)
    class CategoryAdmin(admin.ModelAdmin):
        list_display = ['name', 'slug']
        prepopulated_fields = {'slug': ('name',)}

    @admin.register(Product)
    class ProductAdmin(admin.ModelAdmin):
        list_display = ['name', 'price', 'stock', 'is_available', 'category']
        list_editable = ['price', 'stock', 'is_available']
        prepopulated_fields = {'slug': ('name',)}

    class OrderItemInline(admin.TabularInline):
        model = OrderItem
        extra = 0

    @admin.register(Order)
    class OrderAdmin(admin.ModelAdmin):
        list_display = ['id', 'user', 'status', 'total_price', 'created_at']
        list_editable = ['status']
        inlines = [OrderItemInline]from django.contrib import admin
        from .models import Category, Product, Order, OrderItem

        @admin.register(Category)
        class CategoryAdmin(admin.ModelAdmin):
            list_display = ['name', 'slug']
            prepopulated_fields = {'slug': ('name',)}

        @admin.register(Product)
        class ProductAdmin(admin.ModelAdmin):
            list_display = ['name', 'price', 'stock', 'is_available', 'category']
            list_editable = ['price', 'stock', 'is_available']
            prepopulated_fields = {'slug': ('name',)}

        class OrderItemInline(admin.TabularInline):
            model = OrderItem
            extra = 0

        @admin.register(Order)
        class OrderAdmin(admin.ModelAdmin):
            list_display = ['id', 'user', 'status', 'total_price', 'created_at']
            list_editable = ['status']
            inlines = [OrderItemInline]
