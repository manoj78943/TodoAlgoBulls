from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('task_id', 'title', 'description', 'due_date', 'tags', 'status', 'timestamp')

    def create(self, validated_data):
        title = validated_data.get('title', None)
        description = validated_data.get('description', None)
        status = validated_data.get('status', None)
        
        if title is None or title.strip() == '':
            raise serializers.ValidationError("Title is required.")

        if description is None or description.strip() == '':
            raise serializers.ValidationError("Description is required.")

        if status is None or status.strip() == '':
            raise serializers.ValidationError("Status is required.")
        
        tags_data = validated_data.pop('tags', None)
        if tags_data is not None and tags_data.strip():
            tag_names = [tag.strip() for tag in tags_data.split(',')]
            unique_tags = list(set(tag_names))
            validated_data['tags'] = ', '.join(unique_tags)
        else:
            validated_data['tags'] = None
        
        instance = Task.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        if tags_data is not None and tags_data.strip():
            tag_names = [tag.strip() for tag in tags_data.split(',')]
            unique_tags = list(set(tag_names))
            instance.tags = ', '.join(unique_tags)

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        
        return instance