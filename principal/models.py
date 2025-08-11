from django.db import models


class Cita(models.Model):
    ESTADOS = [
        ('agendada', 'Agendada'),
        ('cancelada', 'Cancelada'),
    ]

    id_cita = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey('Clientes', models.DO_NOTHING, db_column='id_cliente', blank=True, null=True)
    id_empleado = models.ForeignKey('Empleados', models.DO_NOTHING, db_column='id_empleado', blank=True, null=True)
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=50, choices=ESTADOS, blank=True, null=True)  # Esto queda igual
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        cliente = self.id_cliente.nombre if self.id_cliente else 'Sin cliente'
        optometrista = self.id_empleado.nombre if self.id_empleado else 'Sin optometrista'
        return f"Cita #{self.id_cita} - Cliente: {cliente} - Optometrista: {optometrista}"

    class Meta:
        managed = False
        db_table = 'cita'

class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    cedula = models.CharField(unique=True, max_length=20)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'clientes'


class Diagnostico(models.Model):
    id_diagnostico = models.AutoField(primary_key=True)
    id_cita = models.ForeignKey(Cita, models.DO_NOTHING, db_column='id_cita', blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id_cita.id_cliente.nombre} - {self.descripcion[:30]}"


    class Meta:
        managed = False
        db_table = 'diagnostico'


class Empleados(models.Model):
    ROLES = [
    ('optometrista', 'Optometrista'),
    ('recepcionista', 'Recepcionista'),
    ('tecnico', 'Técnico'),
    ('supervisor', 'Supervisor'),
    ]

    id_empleado = models.AutoField(primary_key=True)
    usuario = models.CharField(unique=True, max_length=50)
    contraseña = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    rol = models.CharField(max_length=50, choices=ROLES)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        managed = False
        db_table = 'empleados'


class Evaluacion(models.Model):
    id_evaluacion = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='id_cliente', blank=True, null=True)
    fecha = models.DateField()
    comentario = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'evaluacion'


class Fabricacion(models.Model):
    id_fabricacion = models.AutoField(primary_key=True)
    diagnostico = models.OneToOneField('Diagnostico', on_delete=models.CASCADE)
    tipo_producto = models.CharField(max_length=100)
    formula = models.TextField()
    materiales = models.TextField()
    fecha_entrega_estimada = models.DateField()
    tratamientos = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('en proceso', 'En proceso'),
            ('terminada', 'Terminada'),
            ('cancelada', 'Cancelada')
        ]
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Fabricación #{self.id_fabricacion} - Cliente: {self.diagnostico.id_cita.id_cliente.nombre} - Estado: {self.estado}"


    class Meta:
        managed = False
        db_table = 'fabricacion'

class Reporte(models.Model):
    id_reporte = models.AutoField(primary_key=True)
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_empleado', blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    fecha_generado = models.DateField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        managed = False
        db_table = 'reporte'
