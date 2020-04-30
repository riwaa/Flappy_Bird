import random
import pygame
import sys


class item:
    """this class is for parent class for all objects in the game"""

    def __init__(self, path):
        # load in the image of the item
        self.pic = pygame.image.load(path)
        # get the size of the item
        self.size = self.pic.get_rect().size
        # default position is the starting position
        self.default_position = (0, 0)
        # position is the current position of the object
        self.position = (0, 0)

    def set_default_position(self, position):
        """set the default position of the item"""
        # default position is the starting position
        self.default_position = position
        # position is the current position of the object
        self.position = position

    def display(self, game_display):
        """function to display the image at the position"""
        game_display.blit(self.pic, self.position)


class bird(item):
    """this class is for the bird"""

    def __init__(self, path):
        item.__init__(self, path)
        # setup the initial upward speed, downward speed and gravity
        self.up_v = 10
        self.down_v = 0
        self.gravity = 0.15

    def up(self, game_display):
        """make bird fly upward"""
        # only let the bird fly upward if the there is still more 10% of the bird in the screen
        if self.position[1] >= - self.size[1] * 0.9:
            self.position = (self.position[0], self.position[1] - self.up_v)
            self.display(game_display)

    def down(self, game_display):
        """make bird fly downward"""
        # downward speed will increase by gravity
        self.down_v += self.gravity
        self.position = (self.position[0], self.position[1] + self.down_v)
        self.display(game_display)

    def fly(self, up, game_display):
        """make the bird fly, if the up is true, it will fly up, otherwise fly down"""
        if up:
            self.up(game_display)
            # reset the downward speed after fly up because downwards speed is 0 after flying up
            self.down_v = 0
        else:
            self.down(game_display)

    def oscillating(self, game_display):
        """this is for the game intro
           Bird will drop from the top screen to near its default position
           if bird is below the default position, it fly up
           if bird is above the default position, it will fly down
        """

        if self.position[1] < self.default_position[1]:
            self.fly(False, game_display)
        else:
            self.fly(True, game_display)

    def crash(self, no_go_zone):
        """check if the bird has crash or not"""

        # getting the positions of the no_go_zone
        min_x = no_go_zone[0][0]
        min_y = no_go_zone[0][1]
        max_x = no_go_zone[1][0]
        max_y = no_go_zone[1][1]

        # below is the condition to check for brash
        if (self.position[0] + self.size[0]) >= min_x and self.position[0] <= max_x and \
                (self.position[1] + self.size[1]) >= min_y and self.position[1] <= max_y:
            return True
        else:
            return False


class obstacle(item):
    """create obstacle for the game"""

    def __init__(self, path, velocity):
        item.__init__(self, path)
        """velocity for the obstacle to move to the left"""
        self.left_v = velocity

    def set_out_of_frame_position(self, x_position):
        """ this is the most left position for the obstacle, if it more left, it will be partially out of screen"""
        self.out_of_frame_position = x_position

    def position_reset(self):
        """move the object back to default position after it moves out of screen"""
        if self.position[0] <= self.out_of_frame_position:
            self.position = self.default_position

    def move(self, game_display):
        """move the obstacle"""
        self.position_reset()
        self.position = (self.position[0] - self.left_v, self.position[1])
        self.display(game_display)

    def fence(self):
        """ return up left position and bottom right position"""
        return self.position, (self.position[0] + self.size[0], self.position[1] + self.size[1])


class obstacle_pipe(obstacle):
    """child class of obstacle, design just for pipes"""

    def __init__(self, path, velocity, upper):
        obstacle.__init__(self, path, velocity)

        # if this is an upper pipe, rotate the graph by 180
        self.upper = upper
        if self.upper:
            self.pic = pygame.transform.rotate(self.pic, 180)

    def rand(self, other, gap, base_y, background_y):
        """let two pipe interact with each other since the gap between them has to be constant"""

        # buffer is use so the pipes will never move out of screen
        buffer = 20
        # min is just the buffer
        min_y = buffer
        # max is gap + buffer away from the base
        max_y = (background_y - base_y) - (gap + buffer)
        # randomly generate the position of the upper pipe
        rand_number = random.randint(min_y, max_y)

        upper_y = rand_number - self.size[1]
        lower_y = rand_number + gap

        # reset the default position for both upper and lower pipe
        self.default_position = (self.default_position[0], upper_y)
        other.default_position = (other.default_position[0], lower_y)

    def position_reset(self, other, gap, base_y, background_y):
        """move the object back to default position after it moves out of screen"""
        if self.position[0] <= self.out_of_frame_position:
            # only run the rand function for upper pipe since the function will update for both upper and lower pipe
            if self.upper:
                self.rand(other, gap, base_y, background_y)
            self.position = self.default_position

    def move(self, game_display, other, gap, base_y, background_y):
        """move the obstacle"""
        self.position_reset(other, gap, base_y, background_y)
        self.position = (self.position[0] - self.left_v, self.position[1])
        self.display(game_display)


class display_text:
    """display text during the game"""

    def __init__(self, text):
        self.text = text

    def text_objects(self, font, color=(255, 255, 255)):
        """create the text object"""
        text_surface = font.render(self.text, True, color)
        return text_surface, text_surface.get_rect()

    def message_display(self, game_display, background_size):
        """display the text to the screen"""
        font = pygame.font.Font('freesansbold.ttf', 23)
        text_surface, Text_rect = self.text_objects(font)
        Text_rect.center = ((background_size[0] / 2), (background_size[1] / 2 - 100))
        game_display.blit(text_surface, Text_rect)


class scoring:
    """scoring function for the bird"""

    def __init__(self, bird, upper_pipe):
        self.score = 0

        # load in bird and upper_pipe, they will be used to generate scores
        self.bird = bird
        self.upper_pipe = upper_pipe

        # load in the number image, so it can display nicely
        self.score_pic = [pygame.image.load('figures/'+str(i)+'.png') for i in range(0,10)]
        self.size = self.score_pic[0].get_rect().size

    def addition(self):
        """add 1 to the score if the condition is met"""
        bird_position = self.bird.position[0]
        bird_previous_position = self.bird.position[0] - self.upper_pipe.left_v
        pipe_position = self.upper_pipe.position[0] + self.upper_pipe.size[0]

        # if the bird just clear the pipe, score + 1
        if bird_previous_position <= pipe_position < bird_position:
            self.score += 1

    def display(self, game_display):
        """translate the integer into the animated image and show to screen"""
        self.addition()

        counter = 0
        # loop thru number of the digits for the score and display digit by digit
        for i in str(self.score):
            game_display.blit(self.score_pic[int(i)], (5 + counter*self.size[0], 5))
            counter += 1


class game_engine:

    def __init__(self):
        self.fps = 60
        # velocity for the obstacle
        self.velocity = 2
        # gap between the pipe
        self.gap = 125

    def shell_intro(self):
        """game intro in shell, this will also set the difficulty"""

        print('''
        ----------------------------------------------------------
        Welcome to Flappy Bird. Below are game the game controls:
        Fly the bird: Press Space or Up Arrow key
        Quit: Click the exit botton or press Q
        ----------------------------------------------------------
        ''')

        start = False
        while not start:
            start = True
            difficulty = str(input('''
        Please select your difficulty by typing in 1 to 4:
            e: easy
            n: normal
            h: hard
            l: ludicrous_mode
            q: quit the game. I don't want to have fun\n
            '''))

            # set difficulty based on user's input
            if difficulty == 'e':
                self.gap = 130
            elif difficulty == 'n':
                self.gap = 110
            elif difficulty == 'h':
                self.gap = 90
            elif difficulty == 'l':
                self.velocity = 5
                self.gap = 150
            elif difficulty == 'q':
                pass
            else:
                start = False
                print('please enter correct difficulty level')

        if difficulty == 'q':
            return (False)
        else:
            return (True)

    def start_game(self):

        # initialize pygame, load in game background and initialized pygame windows
        pygame.init()
        game_background = item('figures/background-day.png')
        game_background.set_default_position((0, 0))
        background_size = game_background.size
        game_display = pygame.display.set_mode(background_size)

        # set up the flappy bird, set the default position to middle of the screen
        flappy = bird(path='figures/yellowbird-midflap.png')
        flappy.set_default_position((int(background_size[0] / 2 - flappy.size[0] / 2),
                                     int(background_size[1] / 2 - flappy.size[1] / 2)))
        # change the current position to the top of the screen, so when game begin, the bird will be drop from the top
        flappy.position = (flappy.default_position[0], - flappy.size[1])

        # set up the base, set the default position to the bottom of the screen
        base = obstacle(path='figures/base.png', velocity=self.velocity)
        base.set_default_position((0, background_size[1] - base.size[1]))
        # the most the base should move before moving out of screen is background_x - base_x
        base.set_out_of_frame_position(background_size[0] - base.size[0])

        # set up the upper pipe
        upper_pipe = obstacle_pipe('figures/pipe-green.png', velocity=self.velocity, upper=True)
        # set the default position to the right of the screen where we cannot see it initially,
        upper_pipe.set_default_position((background_size[0],
                                         (background_size[1] - base.size[1]) / 2 - upper_pipe.size[1] - self.gap / 2))
        upper_pipe.set_out_of_frame_position(-upper_pipe.size[0])

        # set up the lower pipe
        lower_pipe = obstacle_pipe(path='figures/pipe-green.png', velocity=self.velocity, upper=False)
        lower_pipe.set_default_position((background_size[0], (background_size[1] - base.size[1]) / 2 + self.gap / 2))
        lower_pipe.set_out_of_frame_position(-lower_pipe.size[0])

        # set up the game over message
        game_over = item('figures/gameover.png')
        game_over.set_default_position(((background_size[0] - game_over.size[0]) / 2,
                                        (background_size[1] - game_over.size[1]) / 2))

        # set up the message I would like to display before the game
        space_message = display_text(text='Press space to continue')

        # set up the game score to track the score
        game_score = scoring(flappy, upper_pipe)

        # set caption and start clock
        pygame.display.set_caption('flappy bird')
        clock = pygame.time.Clock()

        game_intro = True
        crash = False

        while True:

            # grab the user key input
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                # if user click exit or type "Q", quite the game
                if event.type == pygame.QUIT or keys[pygame.K_q]:
                    pygame.quit()
                    sys.exit(0)

            # display game background
            game_background.display(game_display)

            # handling when bird crash
            if crash:
                # display the game over message, and inform user to press Space if want to continue
                game_over.display(game_display)
                space_message.message_display(game_display, background_size)
                base.move(game_display)

                # if user press space or up, re-enter the game loop
                if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
                    # crash = False
                    self.start_game()

            # the main loop if the bird did not crash
            else:
                # game intro
                if game_intro:

                    # move the base, let the bird drop from sky and start oscillating
                    base.move(game_display)
                    flappy.oscillating(game_display)
                    space_message.message_display(game_display, background_size)
                    # if keyboard is pressed, exist the game intro
                    if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
                        game_intro = False

                # main game
                else:

                    # move the upper pipe and also pass in the information needed for the random position generator
                    upper_pipe.move(game_display, lower_pipe, self.gap, base.size[1], background_size[1])

                    # lower pipe does not need to take those arguemnts since the upper pipe will take care of it
                    lower_pipe.move(game_display, None, None, None,None)
                    base.move(game_display)

                    # if space or up key is press, fly upwards. otherwise, fly downward
                    if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
                        fly = True
                    else:
                        fly = False
                    flappy.fly(fly, game_display)

                    # check if the bird crashed or not. Obstacles are base, upper pipe and lower pipe
                    crash = flappy.crash(base.fence()) or flappy.crash(upper_pipe.fence()) or flappy.crash(
                        lower_pipe.fence())

            # display game score
            game_score.display(game_display)

            # update the screen
            pygame.display.update()

            # set the frame per second
            clock.tick(self.fps)


# playing the game!!!
game = game_engine()

if game.shell_intro():
    game.start_game()

quit()
