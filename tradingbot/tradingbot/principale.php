<html>
 <head>
 <meta charset="utf-8">
 <!-- importer le fichier de style -->
 <link rel="stylesheet" href="login_css.css" media="screen" type="text/css" />
 </head>
 <body style='background:#fff;'>
 <div id="content">
 <!-- tester si l'utilisateur est connecté -->
 <?php
 session_start();
 if(isset($_SESSION['username'])){
 $user = $_SESSION['username'];
 // afficher un message
 echo "Bonjour $user, vous êtes connecté<br/><a href='logout.php'>se déconnecter</a>";
 } else {
    echo "Vous êtes déconnecté<br/><a href='login.php'>se connecter</a>";
 }
 ?>
 
 </div>
 </body>
</html>