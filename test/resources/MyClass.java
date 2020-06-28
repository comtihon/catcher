package jtest;

import jtest.OtherClass;

public class MyClass {

    public static void main(String[] args) {
        // works only with {"say": "<name>"}
        String name = args[0].split(":")[1].split("\"")[1];
        System.out.println(new OtherClass("hello " + name).arg);
    }
} 
