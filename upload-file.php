<?php

$upload_dir = "/phptmp/";
$upload_file = $upload_dir . basename($_FILES['file_data']['name']);

//echo $upload_file;

if (!file_exists($_FILES['file_data']['tmp_name'])) {
   echo "FILE NOT FOUND!\n";
}
else {
   echo "FILE EXISTS! Moving to $upload_file\n";
}

if (move_uploaded_file($_FILES['file_data']['tmp_name'], $upload_file)) {
   echo "File good\n";
} 
else  {
   echo "File bad\n";

}

print_r($_POST);
print_r($_FILES);


#phpinfo()
?>
