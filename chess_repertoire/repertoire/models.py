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
        upload_to=constants.OPENING_IMAGE_UPLOAD,
        height_field=constants.OPENING_IMAGE_HEIGHT,
        width_field=constants.OPENING_IMAGE_WIDTH,
        max_length=constants.PATH_MAX_LENGTH
    )

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
            - difficulty: the level of difficulty of the Variation (str)
            - opening: the opening where the Variation belongs (Opening)
            - pgn_file: the PGN file of the Variation (file)
    """

    name = models.CharField(max_length=constants.TEXT_MAX_LENGTH, primary_key=True)
    description = models.CharField(max_length=constants.TEXT_MAX_LENGTH)
    difficulty = models.CharField(
        max_length=constants.TEXT_MAX_LENGTH, blank=False, choices=Opening.Difficulty.choices)
    opening = models.ForeignKey(Opening, on_delete=models.CASCADE)
    pgn_file = models.FileField(upload_to=constants.PGN_UPLOAD, blank=True)

    def __str__(self) -> str:
        return f'{self.name} {self.__class__.__name__} from {self.opening.name}'
    
    def __repr__(self) -> str:
        return f'{super().__repr__()}:{self.__class__.__name__}:{self.name}'

class Line(models.Model):
    """ MODEL::Line
        ---
        Description:
        
        Arguments:
            - move: the move of the Line. (str)
            - name: the name of the Line, if it has one (str)
            - on_turn: the number of the turn of the Line (int)
            - nature: the nature of the Line (str)
            - variation: the Variation from which the Line belongs (Variation)
            - pgn_file: the PGN file of the Line (file)
    """

    class Nature(models.TextChoices):
        """"""
        THEORIC = "THC", "Theoric"
        POSITIONAL = "PST", "Positional"
        TRICKY = "TRC", "Tricky"
        SHARP = "SHP", "Sharp"
        ADVANTAGEOUS = "ADV", "Advantageous"

    move = models.CharField(max_length=constants.MOVE_MAX_LENGTH, primary_key=True)
    name = models.CharField(max_length=constants.TEXT_MAX_LENGTH, blank=True)
    on_turn = models.PositiveIntegerField()
    nature = models.CharField(
        max_length=constants.TEXT_MAX_LENGTH, blank=False, choices=Nature.choices)
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE)
    pgn_file = models.FileField(upload_to=constants.PGN_UPLOAD, blank=True)

    def __str__(self) -> str:
        return f'{self.move} {self.__class__.__name__} from {self.variation.name}'

    def __repr__(self) -> str:
        return f'{super().__repr__()}:{self.__class__.__name__}:{self.move}'