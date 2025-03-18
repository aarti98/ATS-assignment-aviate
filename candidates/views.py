# candidates/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.core.exceptions import ValidationError
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
        query = request.query_params.get('query', '')
        if not query:
            return Response({'message': 'Search query is required'}, status=400)

        # Split query into words and convert to lowercase
        query_words = [word.lower() for word in query.split()]
        
        # Get candidates matching any of the query words
        candidates = self.queryset.filter(
            Q(name__icontains=query_words[0]) |  # First word
            Q(name__icontains=query_words[-1]) |  # Last word
            Q(name__icontains=query_words[1]) if len(query_words) > 2 else Q()  # Middle word if exists
        )

        # Calculate scores for each candidate
        results = []
        for candidate in candidates:
            name_words = candidate.name.lower().split()
            
            # Calculate match criteria
            match_count = sum(1 for word in query_words if word in name_words)
            exact_match = all(word in name_words for word in query_words)
            word_order_score = sum(name_words.index(word) for word in query_words if word in name_words)
            last_name_match = query_words[-1] in name_words[-1]
            first_name_match = query_words[0] in name_words[0]
            
            results.append({
                'candidate': candidate,
                'exact_match': exact_match,
                'match_count': match_count,
                'last_name_match': last_name_match,
                'first_name_match': first_name_match,
                'word_order_score': word_order_score
            })

        # Sort results by:
        # 1. Exact match (True first)
        # 2. Match count (descending)
        # 3. Last name match (True first)
        # 4. First name match (True first)
        # 5. Word order score (lower first)
        # 6. Alphabetical order
        results.sort(key=lambda x: (
            -x['exact_match'],  # True first
            -x['match_count'],  # Higher count first
            -x['last_name_match'],  # True first
            -x['first_name_match'],  # True first
            x['word_order_score'],  # Lower score first
            x['candidate'].name  # Alphabetical order
        ))

        # Return serialized results
        serializer = self.get_serializer([r['candidate'] for r in results], many=True)
        return Response(serializer.data)