from game import Game


def main() -> None:
    # Keep startup logic in one place so launch methods stay consistent.
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
