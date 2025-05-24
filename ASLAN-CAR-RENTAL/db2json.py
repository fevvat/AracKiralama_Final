from app import app, db, User  # app.py'den içe aktarıyoruz
import json

def export_users_to_json():
    with app.app_context():  # Flask context gerekli
        users = User.query.all()
        data = []

        for user in users:
            data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password_hash': user.password_hash,
                'full_name': user.full_name,
                'phone': user.phone,
                'city': user.city,
                'district': user.district,
                'address': user.address,
                'profile_image_url': user.profile_image_url,
                'role': user.role
            })

        with open('users.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print("Kullanıcılar başarıyla users.json dosyasına aktarıldı.")

if __name__ == '__main__':
    export_users_to_json()
