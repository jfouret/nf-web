from yanfui import create_app
import string
import secrets

app = create_app()

if __name__ == '__main__':
    alphabet = string.ascii_letters + string.digits
    MASTER_PASSWORD = ''.join(secrets.choice(alphabet) for i in range(10))
    print(f'Password: {MASTER_PASSWORD}')
    app.run(debug=True)
