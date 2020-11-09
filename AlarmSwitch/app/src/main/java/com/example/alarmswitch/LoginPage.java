package com.example.alarmswitch;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

class User{
    public String username;
    public String password;
    public void User(){

    }
    public void login(String username, String password){
        this.username =  username;
        this.password = password;
    }

}

public class LoginPage extends AppCompatActivity {

    EditText name,pass;
    Button login;
    String username,password;
    User user = new User();
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login_page);

        name=findViewById(R.id.username);
        pass=findViewById(R.id.password);
        login=findViewById(R.id.loginButton);
        login.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                user.login(name.getText().toString(),pass.getText().toString());

                if(user.username.isEmpty() || user.password.isEmpty()){
                    Toast.makeText(LoginPage.this,"Please enter all details",Toast.LENGTH_SHORT).show();
                }else {
                    Intent intent = new Intent(LoginPage.this, MainActivity.class);
                    intent.putExtra("username",user.username);
                    intent.putExtra("password",user.password);
                    startActivity(intent);
                    Log.d("TAG", user.username + "  "+ user.password);

                }
            }
        });
    }
}