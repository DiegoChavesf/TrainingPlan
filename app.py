import json
import flask
import flask_login
from model.kudodto import KudoDto
from model.userdto import UserDto
from model.postdto import PostDto
from model.activitydto import ActivityDto
import sirope

def create_app():
    """
    Crea una aplicación Flask.

    Esta función inicializa la aplicación Flask, configura Flask-Login y configura Sirope.
    Carga la configuración desde un archivo JSON e inicializa Flask-Login.

    Returns:
        tuple: Una tupla que contiene la aplicación Flask, el gestor de inicio de sesión de Flask-Login y una instancia de Sirope.
    """

    lmanager = flask_login.login_manager.LoginManager()
    fapp = flask.Flask(__name__)
    syrp = sirope.Sirope()
    fapp.config.from_file("config.json", load=json.load)
    lmanager.init_app(fapp)
    return fapp, lmanager, syrp
app, lm, srp = create_app()
@lm.user_loader
def user_loader(username):
    """
    Cargar un usuario por nombre de usuario utilizando Sirope.

    Args:
    username (str): El nombre de usuario del usuario a cargar.

    Returns:
        UserDto: El objeto UserDto cargado.
    """

    return UserDto.find(srp, username)

@lm.unauthorized_handler
def unauthorized_handler():
    """
    Manejar el acceso no autorizado.

    Muestra un mensaje de "No autorizado" y redirige a la página de inicio de sesión.

    Returns:
        flask.Response: Una respuesta de redirección a la página de inicio de sesión.
    """

    flask.flash("Unauthorized")
    return flask.redirect("/")


@app.route('/')
def index():
    """
    Renderiza la plantilla login.html.

    Returns:
        La plantilla login.html renderizada.
    """

    return flask.render_template('login.html')

@app.route('/activities')
def activities():
    """
    Renderiza la plantilla activities.html con datos de actividad y comentarios.

    Returns:
        La plantilla activities.html renderizada con datos de actividad y comentarios.
    """

    usr = UserDto.current_user()
    sust = []
    activity_list = list(sirope.Sirope().load_all(ActivityDto))
    for activity in activity_list:
        coments = list(srp.filter(PostDto, lambda p: p._activity_id == activity.__oid__))
        activity.__oid__ = srp.safe_from_oid(activity.__oid__)

        sust.append({
            "activity": activity,
            "coments": coments
        })
    return flask.render_template("activities.html", sust=sust)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Maneja la funcionalidad de inicio de sesión.

    Si el método de solicitud es POST, intenta iniciar sesión con el usuario basado en el nombre de usuario y la contraseña proporcionados.
    Si tiene éxito, redirige a la página de actividades.
    Si no tiene éxito, muestra un mensaje de error y redirige a la página de actividades.
    Si el método de solicitud es GET, renderiza la plantilla login.html.

    Returns:
        Si el inicio de sesión es exitoso, una respuesta de redirección a la página de actividades.
        Si el inicio de sesión no tiene éxito, una respuesta de redirección a la página de actividades.
        Si el método de solicitud es GET, la plantilla login.html renderizada.
    """

    if flask.request.method == 'POST':
        username = flask.request.form.get("logUsername")
        password_txt = flask.request.form.get("logPassword")
        if not username:
            usr = UserDto.current_user()
            if not usr:
                flask.flash("¡Es necesario el login previo!")
                flask.redirect(flask.url_for("activities"))
        else:
           
            if not password_txt:
                flask.flash("¿Y la contraseña?")
                flask.redirect(flask.url_for("activities"))
            usr = UserDto.find(srp, username)
            if not usr:
                flask.flash("Usuario invalido")
                flask.redirect(flask.url_for("activities"))
            elif not usr.chk_password(password_txt):
                flask.flash("Passwords do not match")
            else:
                flask_login.login_user(usr)
                return flask.redirect(flask.url_for('activities'))

    return flask.render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Maneja el registro de usuarios.

    Si el método de solicitud es POST, intenta registrar un nuevo usuario basado en el nombre de usuario, correo electrónico y contraseña proporcionados.
    Si tiene éxito, inicia sesión con el nuevo usuario y redirige a la página de actividades.
    Si no tiene éxito, muestra un mensaje de error y redirige a la página de registro.
    Si el método de solicitud es GET, renderiza el formulario de registro.

    Returns:
        Si el registro es exitoso, una respuesta de redirección a la página de actividades.
        Si el registro no tiene éxito, una respuesta de redirección a la página de registro.
        Si el método de solicitud es GET, el formulario de registro renderizado.
    """

    if flask.request.method == 'POST':
        username = flask.request.form.get("regUsername")
        email_txt = flask.request.form.get("regEmail")
        password_txt = flask.request.form.get("regPassword")
        if not username:
            flask.flash("Nombre de usuario necesario")
            return flask.redirect(flask.url_for("register"))
        if not password_txt:
            flask.flash("Contraseña necesaria")
            return flask.redirect(flask.url_for("register"))
        if not email_txt:
            flask.flash("Email necesaria")
            return flask.redirect(flask.url_for("register"))
        usr = UserDto.find(srp, username)
        if not usr:
            usr = UserDto(username, email_txt, password_txt)
            srp.save(usr)
        flask_login.login_user(usr)
        return flask.redirect(flask.url_for('activities'))
    return flask.render_template("register.html")

@app.route('/profile')
@flask_login.login_required
def profile():
    """
    Renderiza la plantilla profile.html con datos de actividad de usuario.

    Returns:
        La plantilla profile.html renderizada con datos de actividad de usuario.
    """

    sust = []
    usr = UserDto.current_user()
    activities = list(srp.filter(ActivityDto, lambda a: a._user_id == usr.get_id()))
    for activity in activities:
        activity.__oid__ = srp.safe_from_oid(activity.__oid__)
        sust.append({
            "activity": activity,
        })
    return flask.render_template('profile.html', sust=sust)

@app.route('/activity/<activity_id>')
@flask_login.login_required
def activity(activity_id):
    """
    Renderiza la plantilla activity.html con datos de actividad, kudos, publicaciones y usuario.

    Args:
        activity_id (str): El ID de la actividad.

    Returns:
        La plantilla activity.html renderizada con datos de actividad, kudos, publicaciones y usuario.
    """

    sust = {}
    activity_oid = srp.oid_from_safe(activity_id)
    activity = srp.load(activity_oid)
    usr = UserDto.current_user()
    user_kuded = False
    is_author = False
    if activity:
        is_author = usr.get_id() in activity._user_id
        posts = list(srp.filter(PostDto, lambda p: p._activity_id == activity_id))       
        kudos = list(srp.filter(KudoDto, lambda k: k._activity_id == activity.__oid__))       
        for kudo in kudos:
            kudo.__oid__ = srp.safe_from_oid(kudo.__oid__)
            if kudo._user_id == usr.get_id():
                user_kuded = True
                break
        for post in posts:
            post.__oid__ = srp.safe_from_oid(post.__oid__)
        activity.__oid__ = srp.safe_from_oid(activity.__oid__)
        sust = {
            "kudos":kudos,
            "activity_id": activity_id,
            "activity":activity,
            "posts": posts,
            "user": usr,
            "user_kuded": user_kuded,
            "is_author": is_author
        }
        return flask.render_template('activity.html', sust=sust)
    else:
        flask.flash('Activity not found.')
        return flask.redirect(flask.url_for('activities'))

@app.route('/add_activity', methods=['GET', 'POST'])
@flask_login.login_required
def add_activity():
    """
    Maneja la adición de una nueva actividad.

    Si el método de solicitud es POST, intenta agregar una nueva actividad basada en los datos proporcionados.
    Si tiene éxito, redirige a la página de actividades.
    Si no tiene éxito, muestra un mensaje de error.
    Si el método de solicitud es GET, renderiza la plantilla add_activity.html.

    Returns:
        Si la adición de actividad es exitosa, una respuesta de redirección a la página de actividades.
        Si la adición de actividad no tiene éxito, una respuesta de redirección a la página de actividades.
        Si el método de solicitud es GET, la plantilla add_activity.html renderizada.
    """

    if flask.request.method == 'POST':
        has_liked = False
        usr = UserDto.current_user()
        name = flask.request.form.get("acName")
        description = flask.request.form.get("acDescription")
        user_id = usr.get_id()
        kudos = 0
        if not name:
            return flask.redirect(flask.url_for('activities')) 
        new_activity = ActivityDto(name, description, user_id, kudos)
        act_oid = srp.save(new_activity)
        
        srp.save(usr)
        if act_oid:
            return flask.redirect(flask.url_for('activities'))
        else:
            print('Actividad no guardada')
    return flask.render_template('add_activity.html')

@app.route('/edit_activity/<activity_id>', methods=['GET', 'POST'])
@flask_login.login_required
def edit_activity(activity_id):
    """
    Maneja la edición de una actividad existente.

    Args:
        activity_id (str): El ID de la actividad a editar.

    Returns:
        Si la edición de la actividad es exitosa, una respuesta de redirección a la página de detalles de la actividad.
        Si la edición de la actividad no tiene éxito, una respuesta de redirección a la página de actividades.
    """

    activity_oid = srp.oid_from_safe(activity_id)
    activity = srp.load(activity_oid)

    if activity:
        if flask.request.method == 'POST':
            activity._name = flask.request.form.get('acName')
            activity._description = flask.request.form.get('acDescription')
            srp.save(activity)
            flask.flash('Activity updated successfully.')
            return flask.redirect(flask.url_for('activity', activity_id=activity_id))
        return flask.render_template('edit_activity.html', activity=activity)
    else:
        flask.flash('Activity not found.')
        return flask.redirect(flask.url_for('activities'))

@app.route('/delete_activity/<activity_id>', methods=['POST'])
@flask_login.login_required
def delete_activity(activity_id):
    """
    Maneja la eliminación de una actividad y sus publicaciones asociadas.

    Args:
        activity_id (str): El ID de la actividad a eliminar.

    Returns:
        flask.Response: Una respuesta de redirección a la página de perfil.
    """

    activity_oid = srp.oid_from_safe(activity_id)
    activity = srp.load(activity_oid)

    if activity:
        srp.delete(activity_oid)
        posts = list(srp.filter(PostDto, lambda p: p._activity_id == activity_id))
        for post in posts:
            srp.delete(post.__oid__)
        flask.flash('Paper and associated reviews deleted successfully.')
        return flask.redirect(flask.url_for('profile'))
    else:
        flask.flash('Paper not found.')
        return flask.redirect(flask.url_for('profile'))

@app.route('/like_activity/<activity_id>', methods=['POST'])
@flask_login.login_required
def like_activity(activity_id):
    """
    Maneja la acción de dar "me gusta" a una actividad.

    Args:
        activity_id (str): El ID de la actividad a la que se dará "me gusta".

    Returns:
        flask.Response: Una respuesta de redirección a la página de detalles de la actividad.
    """

    activity_oid = srp.oid_from_safe(activity_id)
    activity = srp.load(activity_oid)

    if activity:
        if flask.request.method == 'POST':
            has_liked = True
            usr = UserDto.current_user()
            activity._kudos = activity._kudos + 1
            new_kudo = KudoDto(has_liked, activity_oid, usr.get_id())
            srp.save(activity)
            srp.save(new_kudo)
            flask.flash('Activity updated successfully.')
            return flask.redirect(flask.url_for('activity', activity_id=activity_id, usr_liked=True))
    else:

        flask.flash('Activity not found.')
        return flask.redirect(flask.url_for('activities'))



@app.route('/add_post/<activity_id>', methods=['GET', 'POST'])
@flask_login.login_required
def add_post(activity_id):
    """
    Maneja la adición de una nueva publicación a una actividad.

    Args:
        activity_id (str): El ID de la actividad a la que se agrega la publicación.

    Returns:
        flask.Response: Una respuesta de redirección a la página de detalles de la actividad si la actividad existe.
        flask.Response: Una respuesta de redirección a la página de actividades si la actividad no existe.
    """

    activity_oid = srp.oid_from_safe(activity_id)

    if srp.exists(activity_oid):
        if flask.request.method == 'POST':
            usr = UserDto.current_user()
            content = flask.request.form.get("poContent")
            user_id = usr.get_id()
            new_comment = PostDto(content, activity_id, user_id)
            srp.save(new_comment)
            flask.flash("Comment save")

            return flask.redirect(flask.url_for("activity", activity_id=activity_id))
        return flask.render_template('activities.html')
    else:

        flask.flash('Activity not found.')
        return flask.redirect(flask.url_for('activities'))

@app.route('/logout')
@flask_login.login_required
def logout():
    """
    Cerrar sesión del usuario actual.

    Returns:
        Una respuesta de redirección a la página de inicio de sesión.
    """

    flask_login.logout_user()
    return flask.redirect(flask.url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
