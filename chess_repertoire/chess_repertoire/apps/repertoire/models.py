from pathlib import Path

from django.conf import settings
from django.db import models
from django.urls import reverse

from . import constants


# -- Helper functions -- #
def opening_upload_attribute(opening_instance, filename):
    opening_folder = opening_instance.name.replace(' ', '_').lower()
    filename = f"{opening_folder}{Path(filename).suffix}"
    full_path = Path(settings.MEDIA_ROOT / f'{opening_folder}')
    full_path.mkdir(exist_ok=True, parents=True)
    return f"{opening_folder}/{filename}"

def variation_upload_attribute(variation_instance, filename):
    opening_folder = variation_instance.opening.name.replace(' ', '_').lower()
    variation_folder = variation_instance.name.replace(' ', '_').lower()
    filename = f"{variation_folder}{Path(filename).suffix}"
    full_path = Path(settings.MEDIA_ROOT / f'{opening_folder}/{variation_folder}')
    full_path.mkdir(exist_ok=True, parents=True)
    return f"{opening_folder}/{variation_folder}/{filename}"

# -- Models -- #
class Opening(models.Model):
    """ MODEL::Opening
        ---
        Description: Model describing a Chess Opening

        Arguments:
            - name : name of the Opening (str)
            - color: color of the Opening (int)
            - difficulty: level of difficulty of the Opening (str)
            - category: the type of Opening (str)
            - image : image file identifying the Opening (file)
    """
    class Color(models.IntegerChoices):
        """ CHOICES::Color
            ---
            Description: the color of the Opening: (0 [White], 1 [Black])
        """
        WHITE = 0, "WHITE"
        BLACK = 1, "BLACK"

    class Difficulty(models.TextChoices):
        """ CHOICES::Difficulty
            ---
            Description: the level of difficulty of the Opening.
        """
        EASY = "B", "BEGINNER"
        MEDIUM = "I", "INTERMEDIATE"
        HARD = "A", "ADVANCED",
        EXPERT = "E", "EXPERT"
    
    class Category(models.TextChoices):
        """ CHOICES::Category
            ---
            Description: the type of Opening.
        """
        CLASSIC = "CL", "CLASSIC"
        SYSTEM = "SY", "SYSTEM"
        GAMBIT = "GB", "GAMBIT"
    
    name = models.CharField(max_length=constants.MAX_LENGTH, primary_key=True)
    description = models.TextField(max_length=constants.OPENING_MAX_LENGTH, default='')
    color = models.IntegerField(blank=False, choices=Color.choices)
    difficulty = models.CharField(
        max_length=constants.MAX_LENGTH, blank=False, choices=Difficulty.choices
    )
    category = models.CharField(
        max_length=constants.MAX_LENGTH, blank=False, choices=Category.choices
    )
    image = models.ImageField(
        upload_to=opening_upload_attribute,
        height_field=None,
        width_field=None,
        max_length=constants.FILE_MAX_LENGTH
    )

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('repertoire:opening_detail', kwargs={'pk': self.name})

    def __str__(self) -> str:
        return f'{self.name} {self.__class__.__name__} for {"Black" if self.color else "White"}'

    def __repr__(self) -> str:
        return f'{super().__repr__()}:{self.__class__.__name__}:{self.name}'

class Variation(models.Model):
    """ MODEL::Variation
        ---
        Description: Model describing a Variation of an Opening

        Arguments:
            - name: name of the Variation (str)
            - description: a quick description of the Variation (str)
            - nature: the nature of the Line (str)
            - opening: the opening where the Variation belongs (Opening)
            - pgn_file: the PGN file of the Variation (file)
            - image_file: the image indicating the position on the Board
    """

    class Nature(models.TextChoices):
        """"""
        THEORIC = "THC", "THEORIC"
        POSITIONAL = "PST", "POSITIONAL"
        TRICKY = "TRC", "TRICKY"
        SHARP = "SHP", "SHARP"
        ADVANTAGEOUS = "ADV", "ADVANTAGEOUS"

    name = models.CharField(max_length=constants.MAX_LENGTH, primary_key=True)
    description = models.TextField(max_length=constants.VARIATION_MAX_LENGTH)
    on_turn = models.PositiveIntegerField()
    nature = models.CharField(
        max_length=constants.MAX_LENGTH, blank=False, choices=Nature.choices
    )
    opening = models.ForeignKey(Opening, on_delete=models.CASCADE)
    pgn_file = models.FileField(upload_to=variation_upload_attribute, blank=True)
    image_file = models.ImageField(
        upload_to=variation_upload_attribute,
        height_field=None,
        width_field=None,
        max_length=constants.FILE_MAX_LENGTH
    )

    class Meta:
        ordering = ['-on_turn', 'name']
        unique_together = ['name', 'on_turn']
    
    def get_absolute_url(self):
        return reverse('repertoire:opening_variations', kwargs={'pk': self.opening.name})

    def __str__(self) -> str:
        return f'{self.name} {self.__class__.__name__} from {self.opening.name}'
    
    def __repr__(self) -> str:
        return f'{super().__repr__()}:{self.__class__.__name__}:{self.name}'
