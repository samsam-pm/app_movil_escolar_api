from django.db import transaction
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from app_movil_escolar_api.models import EventoAcademico
from app_movil_escolar_api.serializers import EventoAcademicoSerializer


class EventosAll(generics.CreateAPIView):
    # Obtener todos los eventos académicos
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        eventos = EventoAcademico.objects.all().order_by("id")
        lista = EventoAcademicoSerializer(eventos, many=True).data
        return Response(lista, 200)


class EventosView(generics.CreateAPIView):
    # Obtener, registrar, actualizar y eliminar un evento específico
    permission_classes = (permissions.IsAuthenticated,)

    def get_permissions(self):
        # Permitir POST sin autenticación (como maestros)
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return super().get_permissions()

    # GET: obtener evento por ID
    def get(self, request, *args, **kwargs):
        evento = get_object_or_404(EventoAcademico, id=request.GET.get("id"))
        data = EventoAcademicoSerializer(evento, many=False).data
        return Response(data, 200)

    # POST: registrar nuevo evento
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = EventoAcademicoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Evento académico creado correctamente", "id": serializer.data["id"]},
                201
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT: actualizar evento
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        evento = get_object_or_404(EventoAcademico, id=request.data.get("id"))

        serializer = EventoAcademicoSerializer(evento, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Evento actualizado correctamente",
                "evento": serializer.data
            }, 200)

        return Response(serializer.errors, 400)

    # DELETE: eliminar evento
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        evento = get_object_or_404(EventoAcademico, id=request.GET.get("id"))
        try:
            evento.delete()
            return Response({"details": "Evento eliminado correctamente"}, 200)
        except Exception:
            return Response({"details": "Error al eliminar evento"}, 400)
