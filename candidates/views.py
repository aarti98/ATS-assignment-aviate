# candidates/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Case, When, IntegerField, Value
from .models import Candidate
from .serializers import (
    CandidateCreateSerializer, 
    CandidateUpdateSerializer, 
    CandidateDetailSerializer
)


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CandidateCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CandidateUpdateSerializer
        return CandidateDetailSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'Candidate created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'status': 'success',
            'message': 'Candidate updated successfully',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': 'success',
            'message': 'Candidate deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', '').strip()
        if not query:
            return Response({'message': 'Search query is required'}, status=400)

        query_words = [word.lower() for word in query.split()]
        query_length = len(query_words)

        # Filtering candidates based on query words
        candidates = self.queryset.filter(
            Q(name__icontains=query_words[0]) |
            Q(name__icontains=query_words[-1]) |
            (Q(name__icontains=query_words[1]) if query_length > 2 else Q())
        )

        # Explicit combination scoring logic
        candidates = candidates.annotate(
            full_match=Case(
                When(name__iexact=query, then=Value(6)),  # Highest score for exact match
                default=Value(0),
                output_field=IntegerField()
            ),
            # Explicit two-word combination scoring
            two_word_combo=Case(
                When(name__icontains=' '.join(query_words[:2]), then=Value(5)), 
                When(name__icontains=' '.join([query_words[0], query_words[-1]]), then=Value(4)),
                When(name__icontains=' '.join(query_words[-2:]), then=Value(3)), 
                default=Value(0),
                output_field=IntegerField()
            ),
            # Last name match
            last_name_match=Case(
                When(name__iendswith=query_words[-1], then=Value(2)),
                default=Value(0),
                output_field=IntegerField()
            ),
            # First name match
            first_name_match=Case(
                When(name__istartswith=query_words[0], then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        )

        # Sorting by:
        # 1. Full match
        # 2. Two-word combination matches (explicit order)
        # 3. Last name match
        # 4. First name match
        # 5. Alphabetical order
        candidates = candidates.order_by(
            '-full_match',
            '-two_word_combo',
            '-last_name_match',
            '-first_name_match',
            'name'
        )
        serializer = self.get_serializer(candidates, many=True)
        return Response(serializer.data)
