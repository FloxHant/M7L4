import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

def test_add_existing_user(setup_database, connection):
    """Тест добавления пользователя с уже существующим логином."""
    add_user('testuser', 'testuser2@example.com', 'newpassword')
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username='testuser';")
    count = cursor.fetchone()[0]
    assert count == 1, "Дублирование логина не должно происходить."

def test_authenticate_user_success(setup_database):
    """Тест: успешная аутентификация пользователя."""
    add_user('authuser', 'authuser@example.com', 'securepass')
    result = authenticate_user('authuser', 'securepass')
    assert result, "Пользователь должен успешно пройти аутентификацию."

def test_authenticate_wrong_password(setup_database):
    """Тест: аутентификация с неправильным паролем."""
    add_user('userwrongpass', 'userwrongpass@example.com', 'correctpass')
    result = authenticate_user('userwrongpass', 'wrongpass')
    assert not result, "Аутентификация с неправильным паролем должна возвращать False."
