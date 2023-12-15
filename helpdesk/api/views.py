# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from helpdesk.models import Subject, Ticket
# from .serializers import TicketSerializer

# @api_view(['GET'])
# def get_routes(request):
#     routes = [
#         'GET /api',
#         'GET /api/tickets',
#         'GET /api/tickets/:id'
#     ]
    
#     return Response(routes)


# @api_view(['GET'])
# def get_tickets(request):
#     subjects = Subject.objects.all()
#     serializer = TicketSerializer(subjects, many=True)
    
#     return Response(serializer.data)


# @api_view(['GET'])
# def get_ticket(request, pk):
#     subject = Subject.objects.get(id=pk)
#     serializer = TicketSerializer(subject, many=False)
    
#     return Response(serializer.data)
