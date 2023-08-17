import random
import time
import os
from card_values import CARD_VALUES
from card_imgs import card_imgs, blank_card
from textures import cards_txt, texture1
import pyfiglet
import pygame
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

pygame.mixer.init()
pygame.mixer.music.set_volume(.1)

current_directory = os.path.dirname(__file__)
music_path = os.path.join(current_directory, 'sfx', 'blackjack_loop.mp3')

# SUITS = [
#     f'{Fore.BLACK}{Style.BRIGHT}♠{Fore.WHITE}{Style.NORMAL}',
#     f'{Fore.RED}❤{Fore.WHITE}',
#     f'{Fore.RED}♦{Fore.WHITE}',
#     f'{Fore.BLACK}{Style.BRIGHT}♣{Fore.WHITE}{Style.NORMAL}'
# ]
SUITS = ['♠', '❤', '♦', '♣']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
CARD_FORMATS = {
    '♠': f'{Fore.BLACK}{Style.BRIGHT}♠{Fore.WHITE}{Style.NORMAL}',
    '❤': f'{Fore.RED}❤{Fore.WHITE}',
    '♦': f'{Fore.RED}♦{Fore.WHITE}',
    '♣': f'{Fore.BLACK}{Style.BRIGHT}♣{Fore.WHITE}{Style.NORMAL}'
}


class Card:
    def __init__(self, rank, suit):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f'{self.rank}{self.suit}'


class Deck:
    def __init__(self):
        self.cards = []
        self.used_cards = []

        for suit in SUITS:
            for rank in RANKS:
                new_card = Card(rank, suit)
                self.cards.append(new_card)

    def __str__(self):
        cards_str = ', '.join(str(card) for card in self.cards)
        return f'Deck of {len(self.cards)} cards: {cards_str}'

    def shuffle(self):
        shuffle_count = 100000
        for _ in range(shuffle_count):
            x = random.randint(0, len(self.cards)-1)
            y = random.randint(0, len(self.cards)-1)

            temp = self.cards[x]
            self.cards[x] = self.cards[y]
            self.cards[y] = temp


class Player:
    def __init__(self, name='Player1'):
        self.name = name
        self.hand = []
        self.hand2 = []
        self.total = 0
        self.total2 = 0
        self.score = 0
        self.money = Menu.load_money(self)

    def __str__(self):
        return self.name

    def show_hand(self):
        print(f"{self.name}'s hand:")
        for line in range(7):
            hand_line = '  '.join([card_imgs[str(card)][line] for card in self.hand])
            print(hand_line)
        print()

        if self.hand2: 
            print(f"{self.name}'s second hand: ")
            for line in range(7):
                hand_line = '  '.join([card_imgs[str(card)][line] for card in self.hand2])
                print(hand_line)
            print()

    def pre_deal(self):
        print(f"{self.name}'s hand:")
        for line in range(7):
            hand_line = '  '.join([card_imgs['?'][line] for _ in range(2)])
            print(hand_line)
        print()


class Dealer():
    def __init__(self):
        self.name = 'Dealer'
        self.hand = []
        self.total = 0
        self.score = 0
        self.money = 100000

    def __str__(self):
        return self.name

    def show_hand(self, initial=False):
        card_imgs['?'] = blank_card
        print(f"{self.name}'s hand:")
        for line_num in range(7):
            if initial:
                hand_line = '  '.join([card_imgs['?'][line_num] if index == 0 else card_imgs[str(card)][line_num] for index, card in enumerate(self.hand)])
            else:
                hand_line = '  '.join([card_imgs[str(card)][line_num] for card in self.hand])
            print(hand_line)
        print()

    def pre_deal(self):
        card_imgs['?'] = blank_card
        print(f"{self.name}'s hand:")
        for line_num in range(7):
            hand_line = '  '.join([card_imgs['?'][line_num] for _ in range(2)])
            print(hand_line)
        print()


class Game:
    def __init__(self):
        self.name = 'Blackjack'
        self.deck = Deck()
        self.deck.shuffle()  # <= SHUFFLES THE DECK AT THE BEGINNING OF THE GAME !!!
        while True:
            name = input('\nWhat is your name? > ')
            if name == '':
                self.player = Player()
                break
            if name != '':
                self.player - Player(name)
                break
        self.dealer = Dealer()
        self.pot = 0

    def __str__(self):
        return self.name

    def check_player_money(self):
        if self.player.money <= 0:
            while True:
                get_money = input(
                    "You're out of money. Withdraw more? (y/n) > ").lower()
                if get_money == 'y' or get_money == '':
                    self.player.money += 50
                    Menu.save_money(self, self.player.money)
                    print(f"\nYou received ${Fore.GREEN}50{Fore.WHITE}.\nUpdated wallet: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n")
                    break
                elif get_money == 'n':
                    Menu.save_money(self, self.player.money)
                    break
                else:
                    print("\nIt is suggested that you visit an ATM.\n")

    def place_bet(self, player):
        while True:
            try:
                if player == self.dealer:
                    bet = self.pot  # Match the player's bet
                else:
                    bet = int(input(f"Enter your bet: > $"))

                if 0 <= bet <= player.money:
                    player.money -= bet
                    self.pot += bet
                    break
                else:
                    print("Invalid bet amount. Please enter a valid amount.")
            except ValueError:
                print("Invalid input. Please enter a valid bet amount.")

    def split_hand(self):
        if any(card.rank == self.player.hand[index + 1].rank for index, card in enumerate(self.player.hand[:-1])):
            self.player.hand2.append(self.player.hand.pop())
            self.deal_card(self.player.hand)
            self.deal_card(self.player.hand2)

            self.player.total2 = self.calc_hand(self.player.hand2)
            self.player.total = self.calc_hand(self.player.hand)

    def clear_cards(self):
        self.deck.used_cards.extend(self.player.hand)
        self.deck.used_cards.extend(self.dealer.hand)
        self.player.hand.clear()
        self.dealer.hand.clear()
        if self.player.hand2:
            self.deck.used_cards.extend(self.player.hand2)
            self.player.hand2.clear()

    def deal_card(self, hand):
        if not self.deck.cards:
            print('Reshuffling the deck')  # <= RESHUFFLES DECK WHEN EMPTY
            time.sleep(.5)
            print('...')
            time.sleep(.5)
            self.deck.cards.extend(self.deck.used_cards)
            self.deck.used_cards = []
            self.deck.shuffle()

        card = self.deck.cards.pop(0)
        hand.append(card)

    def play_hand(self):
        self.deal_card(self.player.hand)
        self.deal_card(self.dealer.hand)
        self.deal_card(self.player.hand)
        self.deal_card(self.dealer.hand)
        self.dealer.total = self.calc_hand(self.dealer.hand)
        self.player.total = self.calc_hand(self.player.hand)

        self.dealer.show_hand(initial=True)
        self.dealer.total = self.calc_hand(self.dealer.hand)
        self.player.total = self.calc_hand(self.player.hand)
        self.player.show_hand()
        print(f"{self.player.name}'s total: {Fore.CYAN}{self.player.total}{Fore.WHITE}\n")
        print(f'Current pot: ${Fore.CYAN}{self.pot}{Fore.WHITE}')
        print(f'Current wallet: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')

    def calc_hand(self, hand):
        total = 0
        has_ace = False

        for card in hand:
            rank = card.rank.upper()
            if rank in CARD_VALUES:
                total += CARD_VALUES[rank]
                if rank == 'A':
                    has_ace = True

        if has_ace and total >= 22:
            total -= 10

        return total

    def hit_hand(self, hand, total):
        while total < 21:
            if not self.deck.cards:
                print('No more cards\n')
                break

            if total <= 9:
                hit_input = input(f"Hit on this {Fore.GREEN}{total}{Fore.WHITE} hand?\n[Enter] to hit, [S] to stay > ").lower().strip()
            if total > 9 and total <= 15:
                hit_input = input(f"Hit on this {Fore.YELLOW}{total}{Fore.WHITE} hand?\n[Enter] to hit, [S] to stay > ").lower().strip()
            if total > 15:
                hit_input = input(f"Hit on this {Fore.RED}{total}{Fore.WHITE} hand?\n[Enter] to hit, [S] to stay > ").lower().strip()

            if hit_input == '':
                self.deal_card(hand)
                os.system('clear')

                self.dealer.show_hand(initial=True)
                self.dealer.total = self.calc_hand(self.dealer.hand)
                self.player.total = self.calc_hand(self.player.hand)
                total = self.calc_hand(hand)  # Update the hand total here
                if self.player.hand2:
                    self.player.total2 = self.calc_hand(self.player.hand2)
                self.player.show_hand()
                print(f"{self.player.name}'s total: {Fore.CYAN}{self.player.total}{Fore.WHITE}")
                if self.player.hand2:
                    print(f"{self.player.name}'s 2nd total: {Fore.CYAN}{self.player.total2}{Fore.WHITE}\n")
                print(f'Current pot: ${Fore.CYAN}{self.pot}{Fore.WHITE}')
                print(f'Current wallet: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')
            elif hit_input == 's' or hit_input == 'n':
                print('\n')
                break
            else:
                print('Please enter a valid option')
                print('...')

        return total

    def dealer_hit(self):
        while self.dealer.total < 16:
            if not self.deck.cards:
                print("No more cards")
                break
            self.deal_card(self.dealer.hand)
            os.system('clear')

            self.dealer.show_hand(initial=True)
            self.dealer.total = self.calc_hand(self.dealer.hand)
            self.player.total = self.calc_hand(self.player.hand)

            self.player.show_hand()
            print(f"{self.player.name}'s total: {Fore.CYAN}{self.player.total}{Fore.WHITE}\n")
            if self.player.hand2:
                print(f"{self.player.name}'s 2nd total: {Fore.CYAN}{self.player.total2}{Fore.WHITE}\n")
            print(f'Current pot: ${Fore.CYAN}{self.pot}{Fore.WHITE}')
            print(f'Current wallet: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')

            print('...')
            time.sleep(1)
            if self.dealer.total >= 16:
                break
        return self.dealer.total

    def eval_hands(self):
        self.player.total = self.calc_hand(self.player.hand)
        self.dealer.total = self.calc_hand(self.dealer.hand)
        if self.player.total2 == 0:
            if self.player.total > 21:
                return "Dealer"
            elif self.dealer.total > 21:
                return self.player.name
            elif self.player.total > self.dealer.total:
                return self.player.name
            elif self.dealer.total > self.player.total:
                return "Dealer"
            elif self.player.total == self.dealer.total:
                return "Draw"

        elif self.player.total2 > 0:
            if self.player.total > 21 and self.player.total2 > 21:
                return "Dealer"
            elif self.dealer.total > 21:
                return self.player.name
            elif self.player.total > self.dealer.total or self.player.total2 > self.dealer.total:
                return self.player.name
            elif self.dealer.total > self.player.total and self.dealer.total > self.player.total2:
                return "Dealer"
            elif self.player.total == self.dealer.total and self.player.total2 == self.dealer.total:
                return "Draw"

    def play_game(self):
        play_flag = True
        while play_flag:
            self.player.total = 0
            self.dealer.total = 0
            os.system('clear')

            # print(self.deck)  # <= PRINTS THE WHOLE DECK AT START OF PLAY

            self.dealer.pre_deal()
            self.player.pre_deal()
            print(f"{self.player.name}'s total: {Fore.CYAN}?{Fore.WHITE}")
            print(f'Current wallet: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')

            self.place_bet(self.player)
            self.place_bet(self.dealer)

            os.system('clear')
            self.play_hand()
            if self.player.total <= 21:
                if any(card.rank == self.player.hand[index + 1].rank for index, card in enumerate(self.player.hand[:-1])):
                    split_decision = input("Do you want to split your hand? (y/n) > ").lower().strip()
                    if split_decision != 'n':
                        self.split_hand()
                        os.system('clear')
                        self.dealer.show_hand(initial=True)
                        self.player.show_hand()
                        additional_bet = self.pot / 2  # <= ADDS A SECOND WAGER FOR SECOND HAND
                        self.player.money -= additional_bet
                        Menu.save_money(self, self.player.money)
                        self.pot += additional_bet
                        print(f"{self.player.name}'s total: {Fore.CYAN}{self.player.total}{Fore.WHITE}")
                        if self.player.hand2:
                            print(f"{self.player.name}'s 2nd total: {Fore.CYAN}{self.player.total2}{Fore.WHITE}\n")
                        print(f'Current pot: ${Fore.CYAN}{self.pot}{Fore.WHITE}')
                        print(f'Current wallet: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')
                    else:
                        os. system('clear')
                        self.dealer.show_hand(initial=True)
                        self.player.show_hand()
                        print(f"{self.player.name}'s total: {Fore.CYAN}{self.player.total}{Fore.WHITE}")
                        print(f'Current pot: ${Fore.CYAN}{self.pot}{Fore.WHITE}')
                        print(f'Current wallet: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')

# if player == self.dealer:
#                     bet = self.pot  # Match the player's bet
#                 else:
#                     bet = int(input(f"Enter your bet: > $"))

#                 if 0 <= bet <= player.money:
#                     player.money -= bet
#                     self.pot += bet
#                     break

            if self.player.total < 21:
                self.player.total = self.hit_hand(self.player.hand, self.player.total)
            if self.player.hand2 and self.player.total2 < 21:
                self.player.total2 = self.hit_hand(self.player.hand2, self.player.total2)
            if self.player.total <= 21 and self.dealer.total <= 16:
                self.dealer.total = self.dealer_hit()

            os.system('clear')

            self.dealer.show_hand(initial=False)
            self.dealer.total = self.calc_hand(self.dealer.hand)
            self.player.total = self.calc_hand(self.player.hand)
            if self.dealer.total >= 22:
                dealer_total_color = Fore.RED
            elif self.player.total > 21 and self.player.total2 > 21 and self.dealer.total <= 21:
                dealer_total_color = Fore.GREEN
            elif (self.dealer.total > self.player.total and self.dealer.total <= 21) and (self.dealer.total > self.player.total2 and self.dealer.total <= 21):
                dealer_total_color = Fore.GREEN
            elif (self.dealer.total < self.player.total and self.player.total <= 21) or (self.dealer.total < self.player.total2 and self.player.total <= 21):
                dealer_total_color = Fore.RED
            else:
                dealer_total_color = Fore.RED
            print(f"{self.dealer.name}'s final total: {dealer_total_color}{self.dealer.total}{Fore.WHITE}\n")

            self.player.show_hand()
            if self.player.total >= 22:
                player_total_color = Fore.RED
            if self.dealer.total > 21 and self.player.total <= 21:
                player_total_color = Fore.GREEN
            elif self.player.total > self.dealer.total and self.player.total <= 21:
                player_total_color = Fore.GREEN
            elif self.player.total < self.dealer.total and self.dealer.total <= 21:
                player_total_color = Fore.RED
            else:
                player_total_color = Fore.RED
            print(f"{self.player.name}'s final total: {player_total_color}{self.player.total}{Fore.WHITE}\n")

            if self.player.total2 > 0:
                if self.player.total2 >= 22:
                    player_total2_color = Fore.RED
                if self.dealer.total > 21 and self.player.total2 <= 21:
                    player_total2_color = Fore.GREEN
                elif self.player.total2 > self.dealer.total and self.player.total2 <= 21:
                    player_total2_color = Fore.GREEN
                elif self.player.total2 < self.dealer.total and self.dealer.total <= 21:
                    player_total2_color = Fore.RED
                else:
                    player_total2_color = Fore.RED
                print(f"{self.player.name}'s second final total: {player_total2_color}{self.player.total2}{Fore.WHITE}\n")

            winner = self.eval_hands()
            if winner == f'{self.player.name}':
                self.player.score += 1
                self.player.money += self.pot
                Menu.save_money(self, self.player.money)
                print(f'Winner: {Fore.GREEN}{winner}{Fore.WHITE}!\nReceived {Fore.GREEN}{self.pot}{Fore.WHITE}!\n \nUpdated wallet: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')
                self.pot = 0
            if winner == 'Dealer':
                self.dealer.score += 1
                self.dealer.money += self.pot
                Menu.save_money(self, self.player.money)
                print(f'Winner: {Fore.RED}{winner}{Fore.WHITE}!\nThe house always {Fore.RED}WINS{Fore.WHITE} :(\n \nUpdated wallet: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')
                self.pot = 0
            if winner == 'Draw':
                share_pot = self.pot / 2
                self.player.money += share_pot
                self.dealer.money += share_pot
                Menu.save_money(self, self.player.money)
                print(
                    f'Draw! There is no winner :(\nEach player had a total of {Fore.RED}{self.player.total}{Fore.WHITE}\n')
                self.pot = 0
                print('\n')
            time.sleep(.5)
            print('...\n')

            while True:
                if self.player.money <= 0:
                    self.check_player_money()
                    print('...\n')
                    time.sleep(.5)
                play_again = input(
                    "[Enter] to play again, 'Q' to quit > ").lower().strip()

                if play_again != 'q':
                    os.system('clear')
                    reset_game = pyfiglet.figlet_format(text='Dealing\nNew\nCards!', font='chunky')
                    print(f'\n{reset_game}')
                    time.sleep(.5)
                    Menu.print_texture(self, texture1)
                    time.sleep(.2)
                    print('\n')
                    Menu.print_texture(self, cards_txt)
                    time.sleep(.5)
                    self.clear_cards()
                    Menu.save_money(self, self.player.money)
                    self.player.total = 0
                    self.player.total2 = 0
                    self.dealer.total = 0
                    break

                else:
                    time.sleep(.5)
                    print('\n...\n')
                    time.sleep(.5)
                    Menu.save_money(self, self.player.money)
                    play_flag = False
                    break


class Menu:
    def __init__(self):
        os.system('clear')
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)
        time.sleep(.5)
        welcome_text = pyfiglet.figlet_format(text='Welcome to', font='small')
        print(f'\n{welcome_text}')
        time.sleep(.5)
        game_name_text = pyfiglet.figlet_format(
            text='Blackjack', font='big')
        print(game_name_text)
        time.sleep(1)
        menu_flag = True
        while menu_flag:
            self.print_texture(cards_txt)
            print('\n')
            self.print_texture(texture1)
            menu_text = pyfiglet.figlet_format(text="Menu", font="rectangles")
            print(menu_text)
            print('Options:\n[P]lay game\n[V]iew scores\n[W]allet\n[S]ettings\n[E]xit\n')
            menu_choice = input('Please select an option > ').lower().strip()

            if menu_choice == 'p' or menu_choice == '':
                new_game = Game()
                new_game.play_game()

            if menu_choice == 'v':
                print(f"The Player's score is: {new_game.player.score}")
                print(f"The Dealer's score is: {new_game.dealer.score}")

            if menu_choice == 'w':
                self.display_wallet()

            elif menu_choice == 's':
                time.sleep(.5)
                print('...')
                settings_text = pyfiglet.figlet_format(
                    text="Settings", font="small")
                print(settings_text)
                print('Options:\n[V]olume settings\n[R]ender cards\n[E]xit\n')
                while True:
                    settings_choice = input(
                        'Please select an option > ').lower().strip()
                    if settings_choice == 'v':
                        while True:
                            volume_input = input("Enter volume value (0.0 - 1.0) > ")

                            try:
                                volume = float(volume_input)
                                if 0.0 <= volume <= 1.0:
                                    pygame.mixer.music.set_volume(volume)
                                    print('...')
                                    print(f"Volume set to {Fore.GREEN}{volume}{Fore.WHITE}")
                                    print('...')
                                    time.sleep(.5)
                                    break
                                else:
                                    print('...')
                                    invalid_text = pyfiglet.figlet_format(text='IVALID', font='small')
                                    print(f'{Fore.RED}{invalid_text}')
                                    print("Please enter a value between 0.0 and 1.0.")
                                    print('...')
                                    time.sleep(.5)
                            except ValueError:
                                print('...')
                                invalid_text = pyfiglet.figlet_format(text='IVALID', font='small')
                                print(f'{Fore.RED}{invalid_text}')
                                print(f"{Fore.RED}'VALUE ERROR'{Fore.WHITE}")
                                print('...')
                        break

                    if settings_choice == 'r':
                        print('...')
                        time.sleep(.5)
                        self.view_all_cards()

                    if settings_choice == 'e':
                        break

                    else:
                        invalid_text = pyfiglet.figlet_format(text='IVALID', font='small')
                        print(f'{Fore.RED}{invalid_text}')
                        print('Please enter a valid option.')

            elif menu_choice == 'e':
                exit()

            else:
                invalid_text = pyfiglet.figlet_format(
                    text='IVALID', font='small')
                print(f'{Fore.CYAN}{invalid_text}')
                print('Please enter a valid option')

    def __str__(self):
        return 'Menu'

    def view_all_cards(self):
        print(f'Deck has {Fore.GREEN}{len(card_imgs)}{Fore.WHITE} cards\n')
        for card_name, card_data in card_imgs.items():
            # color_formatted_card_suit = f'{Fore.}'
            print(f"Card: {card_name}")
            for line in card_data.values():
                print(line)
            print()

    def print_texture(self, texture):
        for line_number in texture:
            print(texture[line_number])

    def display_wallet(self):
        with open('player_money.txt', 'r') as file:
            player_money = int(file.read().strip())
        print(f"\nYour available balance: ${Fore.GREEN}{player_money}{Fore.WHITE}\n")

    def save_money(self, money):
        with open('player_money.txt', 'w') as file:
            file.write(str(money))

    def load_money(self):
        with open('player_money.txt', 'r') as file:
            return int(file.read().strip())


if __name__ == "__main__":
    menu = Menu()
