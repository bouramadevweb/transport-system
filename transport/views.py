from django.shortcuts import render, redirect

from .form import InscriptionUtilisateurForm

def inscription_utilisateur(request):
    if request.method == 'POST':
        form = InscriptionUtilisateurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') 
    else:
        form = InscriptionUtilisateurForm()

    return render(request, 'transport/UserInscription.html', {'form': form})