package com.example.alarmswitch;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class LoginPage extends AppCompatActivity {

    EditText name,pass;
    Button login;
    String username,password;

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
                username=name.getText().toString();
                password=pass.getText().toString();

                if(username.isEmpty() || password.isEmpty()){
                    Toast.makeText(LoginPage.this,"Please enter all details",Toast.LENGTH_SHORT).show();
                }else {
                    Intent intent = new Intent(LoginPage.this, MainActivity.class);
                    intent.putExtra("username",username);
                    intent.putExtra("password",password);
                    startActivity(intent);
                    Log.d("TAG", username + "  "+ password);

                }
            }
        });
    }
}