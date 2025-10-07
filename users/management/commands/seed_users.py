from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from faker import Faker  # Para generar nombres y correos falsos

User = get_user_model()


class Command(BaseCommand):
    """
    Comando personalizado de Django para generar usuarios de prueba
    y grupos de la aplicación StreamEvents.
    """
    help = '🌱 Crea usuaris de prova per al desenvolupament'

    def add_arguments(self, parser):
        """
        Define argumentos opcionales que se pueden pasar al comando.
        """
        parser.add_argument('--users', type=int, default=10, help='Nombre d\'usuaris a crear')
        parser.add_argument('--clear', action='store_true', help='Elimina tots els usuaris existents abans de crear-ne de nous')

    def handle(self, *args, **options):
        """
        Método principal que se ejecuta al correr el comando.
        Gestiona la eliminación de usuarios existentes, creación de grupos y creación de usuarios de prueba.
        """
        num_users = options['users']  # Número de usuarios a crear

        # Eliminar usuarios existentes si se pasó la opción --clear
        if options['clear']:
            self.stdout.write('🗑️  Eliminant usuaris existents...')
            count = 0
            # Recorremos todos los usuarios
            for user in User.objects.all():
                if not user.is_superuser:  # No eliminamos superusuarios
                    user.delete()
                    count += 1
            self.stdout.write(self.style.SUCCESS(f'✅ Eliminats {count} usuaris'))

        # Usamos transacción para asegurar que todo se haga correctamente
        with transaction.atomic():
            groups = self.create_groups()  # Crear grupos necesarios
            users_created = self.create_users(num_users, groups)  # Crear usuarios
            
        # Mensaje final indicando éxito
        self.stdout.write(self.style.SUCCESS(f'✅ {users_created} usuaris creats correctament!'))

    def create_groups(self):
        """
        Crea los grupos necesarios si no existen y los devuelve en un diccionario.
        """
        group_names = ['Organitzadors', 'Participants', 'Moderadors']
        groups = {} # Diccionario para almacenar los grupos creados
        
        for name in group_names:
            # get_or_create devuelve el grupo y un booleano que indica si se creó
            group, created = Group.objects.get_or_create(name=name)
            groups[name] = group # Guardamos en el diccionario
            if created:
                # Mensaje indicando que se creó un grupo nuevo
                self.stdout.write(f'  ✓ Grup "{name}" creat')

        return groups

    def create_users(self, num_users, groups):
        """
        Crea usuarios de prueba con Faker y los asigna a grupos.
        """
        users_created = 0
        fake = Faker('es_ES')  # Faker configurado para generar nombres en español

        # Crear superusuario si no existe
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@streamevents.com',
                'first_name': 'Admin',
                'last_name': 'Sistema',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            # Asignamos contraseña segura al superusuario
            admin.set_password('admin123')
            admin.save() # Guardamos cambios en la base de datos
            self.stdout.write('  ✓ Superusuari admin creat')
            users_created += 1 # Sumamos al contador total

        # Crear usuarios normales con datos falsos
        for i in range(1, num_users + 1):
            first_name = fake.first_name()
            last_name = fake.last_name()
            
            # Generamos un username único combinando nombre, apellido y número
            username = f"{first_name.lower()}.{last_name.lower()}{i:03d}".replace(" ", "")
            email = f"{username}@streamevents.com"

            # Asignación de grupos según el índice
            if i % 3 == 0:
                group = groups['Organitzadors']
                role = 'org'
            elif i % 2 == 0:
                group = groups['Moderadors']
                role = 'mod'
            else:
                group = groups['Participants']
                role = 'part'

            # Crear usuario solo si no existe
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                }
            )

            if created:
                user.set_password('password123')  # Contraseña predeterminada
                user.groups.add(group)  # Añadir al grupo correspondiente
                user.save()
                users_created += 1
                self.stdout.write(f'  ✓ Usuari {username} ({role}) creat')
        # Retornamos el total de usuarios creados
        return users_created
