from controller import OTPController
from view import OTPView


def main():
    controller = OTPController()
    view = OTPView(controller)
    view.run()


if __name__ == "__main__":
    main()
