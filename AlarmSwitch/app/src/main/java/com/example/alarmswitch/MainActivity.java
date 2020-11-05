package com.example.alarmswitch;

import android.net.UrlQuerySanitizer;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import androidx.appcompat.app.AppCompatActivity;


import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.RequestBody;

public class MainActivity extends AppCompatActivity {

    private Boolean ALARM_STATUS=true;
    private String url = "http://" + "10.0.2.2" + ":" + 5000 + "/";
    private String postBodyString;
    private MediaType mediaType;
    private RequestBody requestBody;
    private Button alarm;
    private Integer status = 0;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        alarm = findViewById(R.id.alarm_control);
        alarm.setText("STOP");
//        String postBodyText = "{'status': 1}";
//        MediaType mediaType = MediaType.parse("text/plain; charset=utf-8");
//        RequestBody postBody = RequestBody.create(mediaType, postBodyText);
        alarm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                String username = getIntent().getStringExtra("username");
                String password=getIntent().getStringExtra("password");

                try {
                    postRequest("{status:"+status.toString()+",username:"+username+",password: "+password+"}", url);
                    status = (status + 1)%2;
                    if (alarm.getText() == "STOP"){
                        alarm.setText("START");
                    }
                    else{
                        alarm.setText("STOP");
                    }


                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }


        });

    }
    private RequestBody buildRequestBody(JSONObject msg) {
        JSONObject json = msg;
        mediaType = MediaType.parse("application/json; charset=utf-8");
        requestBody = RequestBody.create(String.valueOf(json), mediaType);
        return requestBody;
    }

    private void postRequest(String postBody, String postUrl ) throws JSONException {

            OkHttpClient client = new OkHttpClient();
            JSONObject obj = new JSONObject(postBody);
            RequestBody requestBody = buildRequestBody(obj);

            Log.d("TAG", postBody);
            Request request = new Request.Builder()
                    .post(requestBody)
                    .url(postUrl)
                    .build();

            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(final Call call, final IOException e) {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {

                            Log.d("TAG", url);
                            Toast.makeText(MainActivity.this, "Something went wrong:" + " " + e.getMessage(), Toast.LENGTH_LONG).show();
                            Log.d("TAG","Something went wrong:" + " " + e.getMessage());
                            call.cancel();


                        }
                    });

                }

                @Override
                public void onResponse(Call call, final Response response) throws IOException {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                                 Log.d("TAG", response.+ " ");
                            }
                        }
                    );


                }
            });
        }





}


