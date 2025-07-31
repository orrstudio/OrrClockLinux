from kivy.core.text import LabelBase

def register_fonts():
    """
    Регистрация всех используемых в приложении шрифтов
    """
    # Регистрация шрифтов FontSourceCodePro
    LabelBase.register(
        name='FontSourceCodePro-ExtraLight', 
        fn_regular='fonts/SourceCodePro/SourceCodePro-ExtraLight.ttf'
    )
    LabelBase.register(
        name='FontSourceCodePro-Light', 
        fn_regular='fonts/SourceCodePro/SourceCodePro-Light.ttf'
    )
    LabelBase.register(
        name='FontSourceCodePro-Medium', 
        fn_regular='fonts/SourceCodePro/SourceCodePro-Medium.ttf'
    )
    LabelBase.register(
        name='FontSourceCodePro-Regular', 
        fn_regular='fonts/SourceCodePro/SourceCodePro-Regular.ttf'
    )
    LabelBase.register(
        name='FontSourceCodePro-SemiBold', 
        fn_regular='fonts/SourceCodePro/SourceCodePro-SemiBold.ttf'
    )
    LabelBase.register(
        name='FontSourceCodePro-Bold', 
        fn_regular='fonts/SourceCodePro/SourceCodePro-Bold.ttf'
    )
    LabelBase.register(
        name='FontSourceCodePro-ExtraBold', 
        fn_regular='fonts/SourceCodePro/SourceCodePro-ExtraBold.ttf'
    )
    LabelBase.register(
        name='FontSourceCodePro-Black', 
        fn_regular='fonts/SourceCodePro/SourceCodePro-Black.ttf'
    )

    # Регистрация шрифтов DSEG7Classic
    LabelBase.register(
        name='FontDSEG7-Light', 
        fn_regular='fonts/DSEG-Classic/DSEG7Classic-Light.ttf'
    )
    LabelBase.register(
        name='FontDSEG7-Regular', 
        fn_regular='fonts/DSEG-Classic/DSEG7Classic-Regular.ttf'
    )
    LabelBase.register(
        name='FontDSEG7-Bold', 
        fn_regular='fonts/DSEG-Classic/DSEG7Classic-Bold.ttf'
    )
    LabelBase.register(
        name='FontDSEG14-Light', 
        fn_regular='fonts/DSEG-Classic/DSEG14Classic-Light.ttf'
    )        
    LabelBase.register(
        name='FontDSEG14-Regular', 
        fn_regular='fonts/DSEG-Classic/DSEG14Classic-Regular.ttf'
    )  
    LabelBase.register(
        name='FontDSEG14-Bold', 
        fn_regular='fonts/DSEG-Classic/DSEG14Classic-Bold.ttf'
    )
    LabelBase.register(
        name='DalekBold',
        fn_regular='fonts/RimFonts/DalekPinpointBold.ttf'
    )
    LabelBase.register(
        name='GothicRegular',
        fn_regular='fonts/RimFonts/SawarabiGothic-Regular.ttf'
    )
