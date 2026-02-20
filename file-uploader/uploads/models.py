from django.db import models

class Message(models.Model):
    content = models.TextField()   
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]

class Sim(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    respo=models.JSONField(default=list)
    img=models.ImageField(upload_to='sim_images/', null=True, blank=True)

    def create_simulation(name, description, respo):
        sim=Sim.objects.create(
            name=name,
            description=description,
            respo=respo,
            img=f'sim_images/{name}.jpg'
        )
        sim.save()
        return sim
   
