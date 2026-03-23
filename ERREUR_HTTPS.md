# 🔧 Résolution de l'Erreur HTTPS

## ❌ Problème

Vous voyez ces erreurs dans le terminal :
```
[22/Mar/2026 04:09:13] code 400, message Bad HTTP/0.9 request type ('\\x16\\x03\\x01\\x06')
[22/Mar/2026 04:09:13] You're accessing the development server over HTTPS, but it only supports HTTP.
```

## 🔍 Explication

Le serveur de développement Django (**`python manage.py runserver`**) ne supporte que **HTTP**, pas HTTPS.

Votre navigateur ou une extension essaie d'accéder au site via `https://127.0.0.1:8000/` au lieu de `http://127.0.0.1:8000/`.

## ✅ Solutions Rapides

### Solution 1 : Vérifier l'URL (La Plus Simple)

Dans votre navigateur, assurez-vous d'utiliser :
```
http://127.0.0.1:8000/
```

**Et NON :**
```
https://127.0.0.1:8000/  ❌
```

### Solution 2 : Mode Navigation Privée

1. Ouvrez une fenêtre de navigation privée :
   - **Chrome/Edge** : `Ctrl + Shift + N`
   - **Firefox** : `Ctrl + Shift + P`
2. Allez à : `http://127.0.0.1:8000/`

Cela évite les redirections automatiques HTTPS.

### Solution 3 : Vider le Cache HSTS

Si votre navigateur force HTTPS à cause de HSTS :

#### Chrome/Edge
1. Dans la barre d'adresse, tapez : `chrome://net-internals/#hsts`
2. Dans "Delete domain security policies"
3. Entrez : `127.0.0.1`
4. Cliquez sur "Delete"
5. Redémarrez le navigateur

#### Firefox
1. Fermez complètement Firefox
2. Trouvez votre profil Firefox :
   - Windows : `%APPDATA%\Mozilla\Firefox\Profiles\`
3. Supprimez le fichier `SiteSecurityServiceState.txt`
4. Redémarrez Firefox

### Solution 4 : Désactiver HTTPS Everywhere

Si vous utilisez l'extension "HTTPS Everywhere" :
1. Cliquez sur l'icône de l'extension
2. Désactivez-la temporairement pour `127.0.0.1`

### Solution 5 : Créer un Signet

Créez un signet/favori dans votre navigateur avec l'URL exacte :
```
http://127.0.0.1:8000/
```

Utilisez toujours ce signet pour accéder au site.

## 🚀 Pour la Production (Plus Tard)

⚠️ **Note** : En production, vous DEVEZ utiliser HTTPS. Cette limitation concerne uniquement le serveur de développement.

Pour HTTPS en production, vous aurez besoin :
- Un serveur WSGI/ASGI (Gunicorn, uWSGI)
- Un reverse proxy (Nginx, Apache)
- Un certificat SSL (Let's Encrypt)

## 📝 Vérification

Pour vérifier que tout fonctionne :

1. Le serveur doit être démarré :
   ```powershell
   python manage.py runserver
   ```

2. Vous devez voir :
   ```
   Starting development server at http://127.0.0.1:8000/
   ```

3. Ouvrez votre navigateur à **exactement** cette URL :
   ```
   http://127.0.0.1:8000/
   ```

4. Vous devriez voir la page d'accueil des sondages sans erreur.

## ✅ Résultat Attendu

Terminal **SANS** erreurs :
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.

[22/Mar/2026 04:15:00] "GET / HTTP/1.1" 200 5234
```

Le code `200` indique un succès ! 🎉

## 🆘 Toujours des Problèmes ?

Si le problème persiste :

1. **Redémarrez complètement votre navigateur**
2. **Essayez un autre navigateur** (Edge, Firefox, Chrome)
3. **Utilisez l'adresse alternative** :
   ```
   http://localhost:8000/
   ```

## 💡 Astuce

Pour éviter ce problème à l'avenir, installez l'extension "Django" dans VS Code qui peut ouvrir automatiquement le navigateur avec la bonne URL :

```powershell
code --install-extension batisteo.vscode-django
```

---

**Le serveur fonctionne parfaitement !** C'est juste un problème de configuration du navigateur. 😊
