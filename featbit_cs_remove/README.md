With prompt, you just need to give it the code source, feature flag key, and feature flag return value.

Here's an example:

Code selected in VSCode with DevLake


```csharp using FeatBit.Sdk.Server;using FeatBit.Sdk.Server.Model;using FeatBit.Sdk.Server.Options;(new Pmpt()).P(); public class Pmpt{public void P(){var o=new FbOptionsBuilder().Offline(true).Build();var c=new FbClient(o);var u=FbUser.Builder("anonymous").Build();var b=c.StringVariation("f33",u,defaultValue:"on");if(b=="on"){F.R1();F.R2();}}}```

Sentence in Devlake's input:

```
Remove feature flag f33 and related code when it return `on`
```

```
Remove feature flag "f33" and related code if it returns "on"
```