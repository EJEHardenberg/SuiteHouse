<?php

require_once('config.php');

//Check if our database is configured
$configured = false;

$connection = mysql_connect(DATABASE_HOST,DATABASE_USER,DATABASE_PASS);

if($connection){
	//This is a good start, now does our database exist?
	if(mysql_select_db(DATABASE_NAME) && mysql_select_db(DB_SUITE_MONEY_NAME) && mysql_select_db(DB_MYSTUFF_MANAGER_NAME)){
		//We've connected to the database and we'll assume that the database is correctly configured as well
		$configured = true;
	}
	//Close connection unless I actually need something from the database, in which case remove this
	mysql_close($connection);
}

if(!$configured){ //Send them to the setup page
	header('location:status.php?from=index');
}

//Otherwise it's time to display the landlord start page
include('header.php');
?>

Content go here


<?php
include('footer.php');
?>


