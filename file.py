cat > test_mail.py <<'EOF'
import traceback
from email.mime.image import MIMEImage
from django.conf import settings
from django.core.mail import EmailMessage
from app.models import SystemSettings
from app.tasks import generate_graph

TO = ["Artem.Tutaev@sgs.com"]

print("=== Настройки почты ===")
print("HOST    :", settings.EMAIL_HOST, settings.EMAIL_PORT)
print("USER    :", settings.EMAIL_HOST_USER)
pwd = settings.EMAIL_HOST_PASSWORD or ""
print("PASSWORD:", pwd[:4] + "***" + pwd[-2:] if pwd else "(ПУСТО!)")

try:
    s = SystemSettings.objects.first()
    lang, location = s.notification_language, s.location_name
    print("LANG/LOC:", lang, "/", location)

    if lang == "ru":
        body = f"""
            <p><strong>Добрый день!</strong></p>
            <p>Прилагаем отчет о нарушениях использования средств индивидуальной защиты в {location}.</p>
            <br><img src="cid:graph_image">
            <p>Сообщение выслано автоматически, с уважением команда PPE Guard AI.</p>
            """
    else:
        body = f"""
            <p><strong>Good day!</strong></p>
            <p>We attach a report on violations of the use of personal protective equipment in {location}.</p>
            <br><img src="cid:graph_image">
            <p>This message was sent automatically. Best regards, the PPE Guard AI team.</p>
            """

    print("\nСтрою график из базы...")
    graph_image = generate_graph()

    msg = EmailMessage(f"PPE Guard AI daily Report {location}", body, settings.EMAIL_HOST_USER, TO)
    msg.content_subtype = "html"
    msg.encoding = "utf-8"
    img = MIMEImage(graph_image.getvalue())
    img.add_header("Content-ID", "<graph_image>")
    img.add_header("Content-Disposition", "inline")
    msg.attach(img)

    print("Отправляю на", TO, "...")
    n = msg.send(fail_silently=False)
    print("\n✅ ОТПРАВЛЕНО:", n)
except Exception:
    print("\n❌ ОШИБКА:")
    traceback.print_exc()
EOF
