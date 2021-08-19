from django.db import models
from django.db.models.enums import Choices
from src import constants

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
        WHITE = 0, "White"
        BLACK = 1, "Black"

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
        CLASSIC = "CL", "Classic"
        SYSTEM = "SY", "System"
        GAMBIT = "GB", "Gambit"
    
    name = models.CharField(max_length=constants.TEXT_MAX_LENGTH, primary_key=True)
    color = models.IntegerField(blank=False, choices=Color.choices)
    difficulty = models.CharField(
        max_length=constants.TEXT_MAX_LENGTH, blank=False, choices=Difficulty.choices
    )
    category = models.CharField(
        max_length=constants.TEXT_MAX_LENGTH, blank=False, choices=Category.choices
    )
    image = models.ImageField(
        upload_to=constants.IMAGE_UPLOAD,
        height_field=constants.IMAGE_HEIGHT,
        width_field=constants.IMAGE_WIDTH,
        max_length=constants.PATH_MAX_LENGTH
    )

    class Meta:
        ordering = ['name']

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
        THEORIC = "THC", "Theoric"
        POSITIONAL = "PST", "Positional"
        TRICKY = "TRC", "Tricky"
        SHARP = "SHP", "Sharp"
        ADVANTAGEOUS = "ADV", "Advantageous"

    name = models.CharField(max_length=constants.TEXT_MAX_LENGTH, primary_key=True)
    description = models.CharField(max_length=constants.TEXT_MAX_LENGTH)
    on_turn = models.PositiveIntegerField()
    nature = models.CharField(
        max_length=constants.TEXT_MAX_LENGTH, blank=False, choices=Nature.choices)
    opening = models.ForeignKey(Opening, on_delete=models.CASCADE)
    pgn_file = models.FileField(upload_to=constants.PGN_UPLOAD, blank=True)
    image_file = models.ImageField(
        upload_to=constants.IMAGE_UPLOAD,
        height_field=constants.IMAGE_HEIGHT,
        width_field=constants.IMAGE_WIDTH,
        max_length=constants.PATH_MAX_LENGTH
    )

    class Meta:
        ordering = ['-on_turn', 'name']

    def __str__(self) -> str:
        return f'{self.name} {self.__class__.__name__} from {self.opening.name}'
    
    def __repr__(self) -> str:
        return f'{super().__repr__()}:{self.__class__.__name__}:{self.name}'