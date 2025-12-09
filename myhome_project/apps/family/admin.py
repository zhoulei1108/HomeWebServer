from django.contrib import admin
from .models import Family, FamilyMember, Invitation, UserProfile


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'member_count', 'max_members', 'is_public']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['invite_code', 'created_at', 'updated_at']
    
    def member_count(self, obj):
        return obj.get_member_count()
    member_count.short_description = '成员数量'


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'family', 'role', 'nickname', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__username', 'family__name', 'nickname']
    raw_id_fields = ['user', 'family']


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['family', 'inviter', 'invitee', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['family__name', 'inviter__username', 'invitee__username']
    readonly_fields = ['created_at', 'responded_at', 'expires_at']
    
    actions = ['mark_as_expired']
    
    def mark_as_expired(self, request, queryset):
        queryset.update(status='expired')
    mark_as_expired.short_description = '标记为已过期'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_family', 'notification_enabled', 'email_notifications']
    list_filter = ['notification_enabled', 'email_notifications']
    search_fields = ['user__username']
    raw_id_fields = ['user', 'current_family']