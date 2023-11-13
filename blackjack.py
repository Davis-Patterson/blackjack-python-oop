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
pygame.mixer.music.set_volume(.2)

current_directory = os.path.dirname(__file__)
music_path = os.path.join(current_directory, 'sfx', 'blackjack_loop.mp3')

# SUITS = [
#     f'{Fore.BLACK}{Style.BRIGHT}♠{Fore.WHITE}{Style.NORMAL}',
#     f'{Fore.RED}♥{Fore.WHITE}',
#     f'{Fore.RED}♦{Fore.WHITE}',
#     f'{Fore.BLACK}{Style.BRIGHT}♣{Fore.WHITE}{Style.NORMAL}'
# ]
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
CARD_FORMATS = {
    '♠': f'{Fore.BLACK}{Style.BRIGHT}♠{Fore.WHITE}{Style.NORMAL}',
    '♥': f'{Fore.RED}♥{Fore.WHITE}',
    '♦': f'{Fore.RED}♦{Fore.WHITE}',
    '♣': f'{Fore.BLACK}{Style.BRIGHT}♣{Fore.WHITE}{Style.NORMAL}'
}

if os.name == 'posix':
    refresh = 'clear'
else:
    refresh = 'cls'


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
        self.profit = 0

    def __str__(self):
        return self.name

    def show_hand(self):
        print(f"{Fore.CYAN}{self.name}'s{Fore.WHITE} hand:")
        for line in range(7):
            hand_line = '  '.join([card_imgs[str(card)][line]
                                  for card in self.hand])
            print(hand_line)
        print()

        if self.hand2:
            print(f"{Fore.CYAN}{self.name}'s{Fore.WHITE} second hand: ")
            for line in range(7):
                hand_line = '  '.join([card_imgs[str(card)][line]
                                      for card in self.hand2])
                print(hand_line)
            print()

    def pre_deal(self):
        print(f"{Fore.CYAN}{self.name}'s{Fore.WHITE} hand:")
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
        print(f"{Fore.RED}{self.name}'s{Fore.WHITE} hand:")
        for line_num in range(7):
            if initial:
                hand_line = '  '.join([card_imgs['?'][line_num] if index == 0 else card_imgs[str(
                    card)][line_num] for index, card in enumerate(self.hand)])
            else:
                hand_line = '  '.join(
                    [card_imgs[str(card)][line_num] for card in self.hand])
            print(hand_line)
        print()

    def pre_deal(self):
        card_imgs['?'] = blank_card
        print(f"{Fore.RED}{self.name}'s{Fore.WHITE} hand:")
        for line_num in range(7):
            hand_line = '  '.join([card_imgs['?'][line_num] for _ in range(2)])
            print(hand_line)
        print()


class Game:
    def __init__(self):
        self.name = 'Blackjack'
        self.table_count = 0
        self.table_status = 'neutral'
        while True:
            name = input('\nWhat is your name? > ')
            if name == '':
                self.player = Player()
                break
            if name != '':
                self.player = Player(name)
                break
        self.dealer = Dealer()
        self.pot = 0
        self.deck = Deck()
        self.deck.shuffle()  # <= SHUFFLES THE DECK AT THE BEGINNING OF THE GAME !!!
        self.shuffle_animation()

    def __str__(self):
        return self.name

    def check_player_money(self):
        if self.player.money <= 0:
            while True:
                get_money = input(
                    "You're out of money. Withdraw more? [y/n] > ").lower()
                if get_money == 'y' or get_money == '':
                    self.player.money += 50
                    self.profit += 50
                    Menu.save_money(self, self.player.money)
                    print(
                        f"\nYou received ${Fore.GREEN}50{Fore.WHITE}.\nUpdated wallet: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n")
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
                    bet_str = input("Enter your bet: > $")
                    if bet_str == '':
                        bet = 0
                    else:
                        bet = int(bet_str)

                if 0 <= bet <= player.money:
                    player.money -= bet
                    self.pot += bet
                    break
                else:
                    print("\nInvalid bet amount. Please enter a valid amount.\n")
            except ValueError:
                print("\nInvalid input. Please enter a valid bet amount.\n")

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
            self.shuffle_animation()  # <= RESHUFFLES DECK WHEN EMPTY
            self.table_count = 0  # <= RESETS TABLE COUNT/STATUS
            self.table_status = 'neutral'
            time.sleep(.5)
            print('...')
            time.sleep(.5)
            self.deck.cards.extend(self.deck.used_cards)
            self.deck.used_cards = []
            self.deck.shuffle()

        card = self.deck.cards.pop(0)
        hand.append(card)
        self.calc_table_count(card)
        self.eval_count()
        return card

    def shuffle_animation(self, iterations=3):
        colors = [Fore.RED, Fore.YELLOW, Fore.BLUE,
                  Fore.GREEN, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]

        for _ in range(iterations):
            for color in colors:
                os.system(refresh)
                shuffling_text = pyfiglet.figlet_format(
                    text='Shuffling', font='cybermedium')
                # print(f'{color}{shuffling_text}{Fore.WHITE}')
                print(f'{color}Shuffling the deck!!{Fore.WHITE}')
                time.sleep(.06)
        print()

    def deal_hand(self):
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

        print(
            f"Your hand total: {Fore.CYAN}{self.player.total}{Fore.WHITE}\n")
        if self.table_status == 'very cold':
            print(
                f'Count: {Fore.BLUE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.BLUE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL} :(')
        if self.table_status == 'cold':
            print(
                f'Count: {Fore.CYAN}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Style.BRIGHT}{Fore.CYAN}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
        if self.table_status == 'neutral':
            print(
                f'Count: {Fore.WHITE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.WHITE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
        if self.table_status == 'hot':
            print(
                f'Count: {Fore.RED}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.RED}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
        if self.table_status == 'very hot':
            print(
                f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')
        if self.table_status == 'extremely hot':
            print(
                f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')

        print(f'Current pot: ${Fore.CYAN}{self.pot}{Fore.WHITE}')
        print(
            f'Current wallet: {Style.BRIGHT}${Fore.GREEN}{self.player.money}{Style.NORMAL}{Fore.WHITE}\n')

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
                hit_input = input(
                    f"Hit on this hand with {Fore.GREEN}{total}{Fore.WHITE} total?\n[Enter] to hit, [S] to stay > ").lower().strip()
            if total > 9 and total <= 15:
                hit_input = input(
                    f"Hit on this hand with {Fore.YELLOW}{total}{Fore.WHITE} total?\n[Enter] to hit, [S] to stay > ").lower().strip()
            if total > 15:
                hit_input = input(
                    f"Hit on this hand with {Fore.RED}{total}{Fore.WHITE} total?\n[Enter] to hit, [S] to stay > ").lower().strip()

            if hit_input != 's' and hit_input != 'n':
                self.deal_card(hand)
                os.system(refresh)

                self.dealer.show_hand(initial=True)
                self.dealer.total = self.calc_hand(self.dealer.hand)
                self.player.total = self.calc_hand(self.player.hand)
                total = self.calc_hand(hand)  # Update the hand total here
                if self.player.hand2:
                    self.player.total2 = self.calc_hand(self.player.hand2)
                self.player.show_hand()
                print(
                    f"Your hand total: {Fore.CYAN}{self.player.total}{Fore.WHITE}\n")
                if self.player.hand2:
                    print(
                        f"Your 2nd hand total: {Fore.CYAN}{self.player.total2}{Fore.WHITE}\n")

                if self.table_status == 'very cold':
                    print(
                        f'Count: {Fore.BLUE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.BLUE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL} :(')
                if self.table_status == 'cold':
                    print(
                        f'Count: {Fore.CYAN}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Style.BRIGHT}{Fore.CYAN}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                if self.table_status == 'neutral':
                    print(
                        f'Count: {Fore.WHITE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.WHITE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                if self.table_status == 'hot':
                    print(
                        f'Count: {Fore.RED}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.RED}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                if self.table_status == 'very hot':
                    print(
                        f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')
                if self.table_status == 'extremely hot':
                    print(
                        f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')

                print(f'Current pot: ${Fore.CYAN}{self.pot}{Fore.WHITE}')
                print(
                    f'Current wallet: {Style.BRIGHT}${Fore.GREEN}{self.player.money}{Style.NORMAL}{Fore.WHITE}\n')
            else:
                print('\n')
                break

        return total

    def dealer_hit(self):
        while self.dealer.total < 16:
            if not self.deck.cards:
                print("No more cards")
                break
            self.deal_card(self.dealer.hand)
            os.system(refresh)

            self.dealer.show_hand(initial=True)
            self.dealer.total = self.calc_hand(self.dealer.hand)
            self.player.total = self.calc_hand(self.player.hand)

            self.player.show_hand()
            print(
                f"Your hand total: {Fore.CYAN}{self.player.total}{Fore.WHITE}\n")
            if self.player.hand2:
                print(
                    f"Your 2nd hand total: {Fore.CYAN}{self.player.total2}{Fore.WHITE}\n")

            if self.table_status == 'very cold':
                print(
                    f'Count: {Fore.BLUE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.BLUE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL} :(')
            if self.table_status == 'cold':
                print(
                    f'Count: {Fore.CYAN}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Style.BRIGHT}{Fore.CYAN}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
            if self.table_status == 'neutral':
                print(
                    f'Count: {Fore.WHITE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.WHITE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
            if self.table_status == 'hot':
                print(
                    f'Count: {Fore.RED}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.RED}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
            if self.table_status == 'very hot':
                print(
                    f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')
            if self.table_status == 'extremely hot':
                print(
                    f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')

            print(f'Current pot: ${Fore.CYAN}{self.pot}{Fore.WHITE}')
            print(
                f'Current wallet: {Style.BRIGHT}${Fore.GREEN}{self.player.money}{Style.NORMAL}{Fore.WHITE}\n')

            print('...')
            time.sleep(1)
            if self.dealer.total >= 16:
                break
        return self.dealer.total

    def eval_hands(self):
        self.player.total = self.calc_hand(self.player.hand)
        if self.player.hand2:
            self.player.total2 = self.calc_hand(self.player.hand2)
        self.dealer.total = self.calc_hand(self.dealer.hand)

        if self.player.total2 == 0:
            if self.player.total > 21 and self.dealer.total > 21:
                return "Bust-Draw"
            if self.player.total > 21:
                return "Bust-Loss"
            elif self.dealer.total > 21:
                return self.player.name
            elif self.player.total < 22 and self.dealer.total < 22:
                if self.player.total > self.dealer.total:
                    return self.player.name
                elif self.dealer.total > self.player.total:
                    return "Dealer"
                else:
                    return "Draw"

        elif self.player.total2 > 0:
            if self.player.total > 21 and self.player.total2 > 21:
                return "Bust-Loss"
            elif self.dealer.total > 21:
                return self.player.name
            elif self.player.total > 21 and self.player.total2 < 22 and self.dealer.total < 22:
                if self.player.total2 > self.dealer.total:
                    return self.player.name
                elif self.dealer.total > self.player.total2:
                    return "Dealer"
                else:
                    return "Draw"
            elif self.player.total2 > 21 and self.player.total < 22 and self.dealer.total < 22:
                if self.player.total > self.dealer.total:
                    return self.player.name
                elif self.dealer.total > self.player.total:
                    return "Dealer"
                else:
                    return "Draw"
            elif self.player.total < 22 and self.player.total2 < 22 and self.dealer.total < 22:
                if self.player.total > self.dealer.total or self.player.total2 > self.dealer.total:
                    return self.player.name
                elif self.dealer.total > self.player.total and self.dealer.total > self.player.total2:
                    return "Dealer"
                elif (self.player.total2 < self.player.total and self.player.total == self.dealer.total) or (self.player.total < self.player.total2 and self.player.total2 == self.dealer.total):
                    return "Draw"
                else:
                    return None

    def double_down(self, hand, total, double_down_has_ace):
        while (double_down_has_ace and total < 19) or (not double_down_has_ace and total < 12):
            double_down = input(
                f"Double down on this hand with {Fore.GREEN}{total}{Fore.WHITE} total? [y/n] > ").lower().strip()
            if double_down != 'n':
                self.deal_card(hand)
                additional_bet = self.pot / 2  # <= ADDS A SECOND WAGER FOR SECOND HAND
                self.player.money -= additional_bet
                os.system(refresh)

                self.dealer.show_hand(initial=True)

                self.dealer.total = self.calc_hand(self.dealer.hand)
                self.player.total = self.calc_hand(self.player.hand)
                total = self.calc_hand(hand)  # Update the hand total here
                if self.player.hand2:
                    self.player.total2 = self.calc_hand(self.player.hand2)

                self.player.show_hand()
                print(
                    f"Your hand total: {Fore.CYAN}{self.player.total}{Fore.WHITE}")
                if self.player.hand2:
                    print(
                        f"Your 2nd hand total: {Fore.CYAN}{self.player.total2}{Fore.WHITE}\n")

                if self.table_status == 'very cold':
                    print(
                        f'Count: {Fore.BLUE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.BLUE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL} :(')
                if self.table_status == 'cold':
                    print(
                        f'Count: {Fore.CYAN}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Style.BRIGHT}{Fore.CYAN}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                if self.table_status == 'neutral':
                    print(
                        f'Count: {Fore.WHITE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.WHITE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                if self.table_status == 'hot':
                    print(
                        f'Count: {Fore.RED}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.RED}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                if self.table_status == 'very hot':
                    print(
                        f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')
                if self.table_status == 'extremely hot':
                    print(
                        f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')

                print(f'Current pot: ${Fore.CYAN}{self.pot}{Fore.WHITE}')
                print(
                    f'Current wallet: {Style.BRIGHT}${Fore.GREEN}{self.player.money}{Style.NORMAL}{Fore.WHITE}\n')
                print('...\n')
                time.sleep(.5)
                return True
            else:
                os.system(refresh)

                self.dealer.show_hand(initial=True)

                self.dealer.total = self.calc_hand(self.dealer.hand)
                self.player.total = self.calc_hand(self.player.hand)
                total = self.calc_hand(hand)  # Update the hand total here
                if self.player.hand2:
                    self.player.total2 = self.calc_hand(self.player.hand2)

                self.player.show_hand()
                print(
                    f"Your hand total: {Fore.CYAN}{self.player.total}{Fore.WHITE}")
                if self.player.hand2:
                    print(
                        f"Your 2nd hand total: {Fore.CYAN}{self.player.total2}{Fore.WHITE}\n")

                if self.table_status == 'very cold':
                    print(
                        f'Count: {Fore.BLUE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.BLUE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL} :(')
                if self.table_status == 'cold':
                    print(
                        f'Count: {Fore.CYAN}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Style.BRIGHT}{Fore.CYAN}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                if self.table_status == 'neutral':
                    print(
                        f'Count: {Fore.WHITE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.WHITE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                if self.table_status == 'hot':
                    print(
                        f'Count: {Fore.RED}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.RED}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                if self.table_status == 'very hot':
                    print(
                        f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')
                if self.table_status == 'extremely hot':
                    print(
                        f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')

                print(f'Current pot: ${Fore.CYAN}{self.pot}{Fore.WHITE}')
                print(
                    f'Current wallet: {Style.BRIGHT}${Fore.GREEN}{self.player.money}{Style.NORMAL}{Fore.WHITE}\n')
                print('...\n')
                return False

    def calc_table_count(self, card):
        rank = card.rank
        if rank in ['A', 'K', 'Q', 'J', '10']:
            self.table_count -= 1
        elif rank in ['7', '8', '9']:
            pass
        elif rank in ['1', '2', '3', '4', '5', '6']:
            self.table_count += 1
        else:
            print("Can't update count")

    def eval_count(self):
        if self.table_count < -5:
            self.table_status = 'very cold'
        elif -5 <= self.table_count <= -1:
            self.table_status = 'cold'
        elif 0 <= self.table_count <= 0:
            self.table_status = 'neutral'
        elif 1 <= self.table_count <= 4:
            self.table_status = 'hot'
        elif 4 <= self.table_count < 6:
            self.table_status = 'very hot'
        else:
            self.table_status = 'extremely hot'

    def play_game(self):
        play_flag = True
        double_down_flag = False
        double_down_flag2 = False
        while play_flag:
            self.player.total = 0
            self.dealer.total = 0
            os.system(refresh)

            # print(self.deck)  # <= PRINTS THE WHOLE DECK AT START OF PLAY

            self.dealer.pre_deal()
            self.player.pre_deal()
            print(f"Your hand total: {Fore.CYAN}?{Fore.WHITE}\n")

            if self.table_status == 'very cold':
                print(
                    f'Count: {Fore.BLUE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.BLUE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL} :(')
            if self.table_status == 'cold':
                print(
                    f'Count: {Fore.CYAN}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Style.BRIGHT}{Fore.CYAN}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
            if self.table_status == 'neutral':
                print(
                    f'Count: {Fore.WHITE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.WHITE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
            if self.table_status == 'hot':
                print(
                    f'Count: {Fore.RED}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.RED}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
            if self.table_status == 'very hot':
                print(
                    f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')
            if self.table_status == 'extremely hot':
                print(
                    f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')

            print(
                f'Current wallet: {Style.BRIGHT}${Fore.GREEN}{self.player.money}{Style.NORMAL}{Fore.WHITE}\n')

            self.place_bet(self.player)
            self.place_bet(self.dealer)

            os.system(refresh)

            self.deal_hand()

            if self.player.total <= 21:
                if any(card.rank == self.player.hand[index + 1].rank for index, card in enumerate(self.player.hand[:-1])):
                    split_decision = input(
                        "Do you want to split your hand? [y/n] > ").lower().strip()
                    if split_decision != 'n':
                        self.split_hand()
                        os.system(refresh)

                        self.dealer.show_hand(initial=True)
                        self.player.show_hand()
                        additional_bet = self.pot / 2  # <= ADDS A SECOND WAGER FOR SECOND HAND
                        self.player.money -= additional_bet
                        Menu.save_money(self, self.player.money)
                        self.pot += additional_bet
                        print(
                            f"Your hand total: {Fore.CYAN}{self.player.total}{Fore.WHITE}")
                        if self.player.hand2:
                            print(
                                f"Your 2nd hand total: {Fore.CYAN}{self.player.total2}{Fore.WHITE}\n")

                        if self.table_status == 'very cold':
                            print(
                                f'Count: {Fore.BLUE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.BLUE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL} :(')
                        if self.table_status == 'cold':
                            print(
                                f'Count: {Fore.CYAN}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Style.BRIGHT}{Fore.CYAN}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                        if self.table_status == 'neutral':
                            print(
                                f'Count: {Fore.WHITE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.WHITE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                        if self.table_status == 'hot':
                            print(
                                f'Count: {Fore.RED}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.RED}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                        if self.table_status == 'very hot':
                            print(
                                f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')
                        if self.table_status == 'extremely hot':
                            print(
                                f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')

                        print(
                            f'Current pot: ${Fore.CYAN}{self.pot}{Fore.WHITE}')
                        print(
                            f'Current wallet: {Style.BRIGHT}${Fore.GREEN}{self.player.money}{Style.NORMAL}{Fore.WHITE}\n')
                        print('...\n')
                    else:
                        os. system('clear')
                        self.dealer.show_hand(initial=True)
                        self.player.show_hand()
                        print(
                            f"Your hand total: {Fore.CYAN}{self.player.total}{Fore.WHITE}")

                        if self.table_status == 'very cold':
                            print(
                                f'Count: {Fore.BLUE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.BLUE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL} :(')
                        if self.table_status == 'cold':
                            print(
                                f'Count: {Fore.CYAN}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Style.BRIGHT}{Fore.CYAN}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                        if self.table_status == 'neutral':
                            print(
                                f'Count: {Fore.WHITE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.WHITE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                        if self.table_status == 'hot':
                            print(
                                f'Count: {Fore.RED}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.RED}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.')
                        if self.table_status == 'very hot':
                            print(
                                f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')
                        if self.table_status == 'extremely hot':
                            print(
                                f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}')

                        print(
                            f'Current pot: ${Fore.CYAN}{self.pot}{Fore.WHITE}')
                        print(
                            f'Current wallet: {Style.BRIGHT}${Fore.GREEN}{self.player.money}{Style.NORMAL}{Fore.WHITE}\n')
                        print('...\n')

            double_down_has_ace = False
            for card in self.player.hand:
                rank = card.rank.upper()
                if rank == 'A':
                    double_down_has_ace = True

            if double_down_has_ace:
                if self.player.total < 19:
                    #  FIRST DOUBLE DOWN SEQUENCE
                    double_down_flag = self.double_down(self.player.hand,
                                                        self.player.total, double_down_has_ace)
            if not double_down_has_ace:
                if self.player.total < 12:
                    double_down_flag = self.double_down(self.player.hand,
                                                        self.player.total, double_down_has_ace)

            double_down_has_ace2 = False
            for card in self.player.hand2:
                rank = card.rank.upper()
                if rank == 'A':
                    double_down_has_ace2 = True

            if self.player.hand2:
                if double_down_has_ace2:
                    if self.player.total2 < 19:
                        #  FIRST DOUBLE DOWN SEQUENCE
                        double_down_flag2 = self.double_down(
                            self.player.hand2, self.player.total2, double_down_has_ace)

                if not double_down_has_ace2:
                    if self.player.total2 < 12:
                        double_down_flag2 = self.double_down(
                            self.player.hand2, self.player.total2, double_down_has_ace)

            if not double_down_flag:
                if self.player.total < 21:
                    self.player.total = self.hit_hand(
                        self.player.hand, self.player.total)
            if not double_down_flag2:
                if self.player.hand2:
                    if self.player.total2 < 21:
                        self.player.total2 = self.hit_hand(
                            self.player.hand2, self.player.total2)

            if (self.player.total <= 21 and self.dealer.total <= 16) or (self.player.total2 <= 21 and self.dealer.total <= 16):
                self.dealer.total = self.dealer_hit()

            os.system(refresh)

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
            print(
                f"{self.dealer.name}'s final total: {dealer_total_color}{self.dealer.total}{Fore.WHITE}\n")

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
            print(
                f"Your final hand total: {player_total_color}{self.player.total}{Fore.WHITE}\n")

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
                print(
                    f"Your 2nd final total: {player_total2_color}{self.player.total2}{Fore.WHITE}\n")

            if self.table_status == 'very cold':
                print(
                    f'Count: {Fore.BLUE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.BLUE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL} :(\n')
            if self.table_status == 'cold':
                print(
                    f'Count: {Fore.CYAN}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Style.BRIGHT}{Fore.CYAN}{self.table_status}{Fore.WHITE}{Style.NORMAL}.\n')
            if self.table_status == 'neutral':
                print(
                    f'Count: {Fore.WHITE}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.WHITE}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.\n')
            if self.table_status == 'hot':
                print(
                    f'Count: {Fore.RED}{Style.BRIGHT}{self.table_count}{Fore.WHITE}{Style.NORMAL} table is {Fore.RED}{Style.BRIGHT}{self.table_status}{Fore.WHITE}{Style.NORMAL}.\n')
            if self.table_status == 'very hot':
                print(
                    f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}\n')
            if self.table_status == 'extremely hot':
                print(
                    f'{Style.BRIGHT}Count: {Fore.RED}{self.table_count}{Fore.WHITE} table is {Fore.RED}{self.table_status}{Fore.WHITE}!!{Style.NORMAL}\n')

            winner = self.eval_hands()
            if winner == f'{self.player.name}':
                self.player.score += 1
                self.player.profit += self.pot
                self.player.money += self.pot
                Menu.save_money(self, self.player.money)
                print(f'Winner: {Fore.GREEN}{winner}{Fore.WHITE}!\nReceived ${Fore.GREEN}{self.pot}{Fore.WHITE}!\n \nUpdated wallet: +${Fore.GREEN}{self.pot}{Fore.WHITE} total: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')
                self.pot = 0
            if winner == 'Dealer':
                self.dealer.score += 1
                self.dealer.money += self.pot
                self.player.profit -= self.pot
                Menu.save_money(self, self.player.money)
                print(
                    f'Winner: {Fore.RED}{winner}{Fore.WHITE}!\nThe house always wins :(\n \nUpdated wallet: -${Fore.RED}{self.pot / 2}{Fore.WHITE} total: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')
                self.pot = 0
            if winner == 'Draw':
                share_pot = self.pot / 2
                self.player.money += share_pot
                self.player.profit += share_pot
                self.dealer.money += share_pot
                Menu.save_money(self, self.player.money)
                print(
                    f'Draw! There is no winner :(\nUpdated wallet: +${Fore.GREEN}{self.pot / 2}{Fore.WHITE} total: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')
                self.pot = 0
            if winner == 'Bust-Loss':
                self.dealer.score += 1
                self.dealer.money += self.pot
                self.player.profit -= self.pot
                Menu.save_money(self, self.player.money)
                print(
                    f'Bust! The house always wins :(\nUpdated wallet: -${Fore.RED}{self.pot / 2}{Fore.WHITE} total: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')
                self.pot = 0
            if winner == 'Bust-Draw':
                share_pot = self.pot / 2
                self.player.money += share_pot
                self.player.profit += share_pot
                self.dealer.money += share_pot
                Menu.save_money(self, self.player.money)
                print(
                    f'Bust! There is no winner :(\nUpdated wallet: +${Fore.GREEN}{self.pot / 2}{Fore.WHITE} total: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')
                self.pot = 0
            if winner is None:
                share_pot = self.pot / 2
                self.player.money += share_pot
                self.player.profit += share_pot
                self.dealer.money += share_pot
                Menu.save_money(self, self.player.money)
                print(
                    f'Could not determine a winner.\nRound {Fore.RED}terminated{Fore.WHITE} :(\nUpdated wallet: +${Fore.GREEN}{self.pot / 2}{Fore.WHITE} total: ${Fore.GREEN}{self.player.money}{Fore.WHITE}\n')
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
                    os.system(refresh)

                    reset_game = pyfiglet.figlet_format(
                        text='Dealing\nNew\nCards!', font='chunky')
                    print(f'\n{reset_game}')
                    time.sleep(.25)
                    Menu.print_texture(self, texture1)
                    time.sleep(.25)
                    print('\n')
                    Menu.print_texture(self, cards_txt)
                    time.sleep(.25)
                    self.clear_cards()
                    double_down_flag = False
                    double_down_flag2 = False
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
        os.system(refresh)

        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # <= TURN MUSIC ON AND OFF

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
            print(
                'Options:\n[P]lay game\n[V]iew scores\n[W]allet\n[S]ettings\n[E]xit\n')
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
                print(
                    'Options:\n[V]olume settings\n[R]ender cards\n[S]huffle Animation\n[E]xit\n')
                while True:
                    settings_choice = input(
                        'Please select an option > ').lower().strip()
                    if settings_choice == 'v' or settings_choice == '':
                        while True:
                            volume_input = input(
                                "Enter volume value (0.0 - 1.0) > ")
                            if volume_input == '':
                                volume_input == 0.0
                            try:
                                volume = float(volume_input)
                                if 0.0 <= volume <= 1.0:
                                    pygame.mixer.music.set_volume(volume)
                                    print('...')
                                    print(
                                        f"Volume set to {Fore.GREEN}{volume}{Fore.WHITE}")
                                    print('...')
                                    time.sleep(.5)
                                    break
                                else:
                                    print('...')
                                    invalid_text = pyfiglet.figlet_format(
                                        text='IVALID', font='small')
                                    print(f'{Fore.RED}{invalid_text}')
                                    print(
                                        "Please enter a value between 0.0 and 1.0.")
                                    print('...')
                                    time.sleep(.5)
                            except ValueError:
                                print('...')
                                invalid_text = pyfiglet.figlet_format(
                                    text='IVALID', font='small')
                                print(f'{Fore.RED}{invalid_text}')
                                print(f"{Fore.RED}'VALUE ERROR'{Fore.WHITE}")
                                print('...')
                        break

                    if settings_choice == 'r':
                        print('...')
                        time.sleep(.5)
                        self.view_all_cards()

                    if settings_choice == 's':
                        animation_flag = True
                        while animation_flag:
                            Game.shuffle_animation(self)
                            loop_animation = input(
                                'Replay? [y/n] >').strip().lower()
                            if loop_animation != 'n':
                                continue
                            else:
                                animation_flag = False
                                break
                        break

                    if settings_choice == 'e':
                        break

                    else:
                        invalid_text = pyfiglet.figlet_format(
                            text='IVALID', font='small')
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
        print(
            f'Deck has {Fore.GREEN}{len(card_imgs)-1}{Fore.WHITE} cards +1 blank card\n')
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
            player_money = float(file.read().strip())
        print(
            f"\nYour available balance: {Style.BRIGHT}${Fore.GREEN}{player_money}{Style.NORMAL}{Fore.WHITE}\n")

    def save_money(self, money):
        with open('player_money.txt', 'w') as file:
            file.write(str(money))

    def load_money(self):
        with open('player_money.txt', 'r') as file:
            return float(file.read().strip())


if __name__ == "__main__":
    menu = Menu()
