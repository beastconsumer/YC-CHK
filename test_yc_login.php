<?php
// Testa via curl primeiro (sem Selenium)
error_reporting(0);
$email = "anushasheguri"; $pass = "2ht.5.tC7DXvSVu";

$ch = curl_init(); $jar = tempnam(sys_get_temp_dir(), "yc_");
curl_setopt_array($ch, [CURLOPT_COOKIEJAR=>$jar, CURLOPT_COOKIEFILE=>$jar, CURLOPT_RETURNTRANSFER=>1, CURLOPT_SSL_VERIFYPEER=>0, CURLOPT_TIMEOUT=>15, CURLOPT_FOLLOWLOCATION=>1, CURLOPT_HEADER=>0]);
$ua = "Mozilla/5.0";

// GET login page
curl_setopt_array($ch, [CURLOPT_URL=>"https://account.ycombinator.com/", CURLOPT_POST=>0, CURLOPT_HTTPHEADER=>["User-Agent: $ua"]]);
$r = curl_exec($ch); curl_close($ch);

// Extract CSRF
preg_match('/name="csrf-token"\s*content="([^"]+)"/', $r, $csrf);
preg_match('/name="authenticity_token"\s*value="([^"]+)"/', $r, $at);
$token = $csrf[1] ?? $at[1] ?? "";
echo "Token: " . ($token ? "YES" : "NO") . "\n";

// Try Rails API login
$ch2 = curl_init("https://account.ycombinator.com/sign_in");
curl_setopt_array($ch2, [CURLOPT_COOKIEJAR=>$jar2=tempnam(sys_get_temp_dir(),"yc2_"), CURLOPT_COOKIEFILE=>$jar2, CURLOPT_RETURNTRANSFER=>1, CURLOPT_SSL_VERIFYPEER=>0, CURLOPT_TIMEOUT=>15, CURLOPT_FOLLOWLOCATION=>1, CURLOPT_HEADER=>0, CURLOPT_POST=>1, CURLOPT_POSTFIELDS=>http_build_query(["user[email]"=>$email,"user[password]"=>$pass,"authenticity_token"=>$token,"commit"=>"Sign+in"]), CURLOPT_HTTPHEADER=>["Content-Type: application/x-www-form-urlencoded","User-Agent: $ua","Referer: https://account.ycombinator.com/"]]);
$r2 = curl_exec($ch2);
$eff = curl_getinfo($ch2, CURLINFO_EFFECTIVE_URL);
echo "Final URL: $eff\n";
echo "Size: " . strlen($r2) . "\n";
echo "Has 'sign_in': " . (stripos($r2,"sign_in")!==false?"YES":"NO")."\n";
echo "Has 'startupschool': " . (stripos($r2,"startupschool")!==false?"YES":"NO")."\n";
curl_close($ch2);
@unlink($jar); @unlink($jar2);
