# Snix

Snix is a C-like programming language for creating Allegorithmic Substance
Designer functions through code instead of nodes. Very useful when wanting
to create more complex functions or converting GLSL shader code to
Substance Designer functions.

Powered by [Snixel](https://github.com/krista-koivisto/snixel).

### Sample

```
float DegToRad(float angle)
{
    float pi = 3.14159f;
    return (angle * pi / 180.0f);
}

float RadToDeg(float rad)
{
    float pi = 3.14159f;
    return rad * 180.0f / pi;
}
```
