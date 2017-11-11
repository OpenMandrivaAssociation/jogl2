%{?_javapackages_macros:%_javapackages_macros}

Name:           jogl2
Epoch:          2
Version:        2.3.2
Release:        5.1
%global src_name jogl-v%{version}
Summary:        Java bindings for the OpenGL API

Group:          Development/Java
# For a breakdown of the licensing, see LICENSE.txt 
License:        BSD and MIT and ASL 2.0 and ASL 1.1 
URL:            http://jogamp.org/
Source0:        http://jogamp.org/deployment/v%{version}/archive/Sources/%{src_name}.tar.xz
Source1:        %{name}-pom.xml

Patch2:         %{name}-0002-deactivate-debug-printf.patch
Patch3:         %{name}-0003-delete-not-supported-API.patch
Patch4:         %{name}-0004-disable-some-tests.patch
Patch5:         %{name}-add-secarchs.patch

BuildRequires:  java-devel
BuildRequires:  jpackage-utils
BuildRequires:  gluegen2-devel = %{version}
BuildRequires:  eclipse-swt
BuildRequires:  pkgconfig(xt)
BuildRequires:  pkgconfig(xrender)
BuildRequires:  pkgconfig(xxf86vm)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  pkgconfig(xcursor)
BuildRequires:  maven-local

Requires:       java
Requires:       jpackage-utils
Requires:       gluegen2 = %{version}

%description
The JOGL project hosts the development version of the Java Binding for
the OpenGL API (JSR-231), and is designed to provide hardware-supported 3D
graphics to applications written in Java. JOGL provides full access to the
APIs in the OpenGL 2.0 specification as well as nearly all vendor extensions,
and integrates with the AWT and Swing widget sets. It is part of a suite of
open-source technologies initiated by the Game Technology Group at
Sun Microsystems.

%package doc
Summary:        User manual for jogl2
Group:          Documentation
BuildArch:      noarch

%description doc
User manual for jogl2.

%prep
%setup -n %{src_name}

%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

# Remove bundled dependencies
find -name "*.jar" -type f -exec rm {} \;
find -name "*.apk" -type f -exec rm {} \;
rm -fr make/lib

# Restore the gluegen2 source code from gluegen2-devel
rm -fr ../gluegen
cp -rdf %{_datadir}/gluegen2 ../gluegen

# Fix file-not-utf8
for file in README.txt; do
    iconv -f ISO-8859-1 -t UTF-8 -o $file.new $file && \
    touch -r $file $file.new && \
    mv $file.new $file
done

# git executable should not be used, use true (to avoid checkout) instead
sed -i 's/executable="git"/executable="true"/' make/build-common.xml

%build
cd make

# As we never cross-compile this package, the SDK root is always /
export TARGET_PLATFORM_ROOT=/

xargs -t ant <<EOF
 -verbose
 -Dc.compiler.debug=true
 -Djavacdebug=true
 -Djavac.memorymax=512m
 -Dcommon.gluegen.build.done=true
 
 -Dantlr.jar=%{_javadir}/antlr.jar 
 -Djunit.jar=%{_javadir}/junit.jar 
 -Dant.jar=%{_javadir}/ant.jar 
 -Dant-junit.jar=%{_javadir}/ant/ant-junit.jar 
 -Dgluegen.jar=%{_javadir}/gluegen2.jar 
 -Dgluegen-rt.jar=%{_jnidir}/gluegen2-rt.jar 
 -Dswt.jar=%{_jnidir}/swt.jar

 -Djava.excludes.all='com/jogamp/newt/util/applet*/**/*.java com/jogamp/audio/**/*.java jogamp/opengl/gl2/fixme/**/*.java com/jogamp/opengl/test/**/*.java'

 -Djavadoc.link=%{_javadocdir}/java 
 -Dgluegen.link=%{_javadocdir}/gluegen2 
 
 build.nativewindow build.jogl build.newt one.dir javadoc.public
EOF

%install
mkdir -p %{buildroot}%{_javadir}/%{name} \
    %{buildroot}%{_libdir}/%{name} \
    %{buildroot}%{_jnidir}

install build/jar/jogl-all.jar %{buildroot}%{_jnidir}/%{name}.jar
ln -s ../../..%{_jnidir}/%{name}.jar %{buildroot}%{_libdir}/%{name}/
install -t %{buildroot}%{_libdir}/%{name}/ build/lib/*.so

# Provide JPP pom
mkdir -p %{buildroot}%{_mavenpomdir}
install -pm 644 %{SOURCE1} %{buildroot}%{_mavenpomdir}/JPP-%{name}.pom
%add_maven_depmap JPP-%{name}.pom %{name}.jar -a "org.jogamp.jogl:jogl-all"

# Make the doc package
mkdir -p %{buildroot}%{_docdir}/%{name}
cp -rdf doc/* %{buildroot}%{_docdir}/%{name}
cp -t %{buildroot}%{_docdir}/%{name}/ README.txt LICENSE.txt CHANGELOG.txt

%files -f .mfiles
%{_docdir}/%{name}/README.txt
%{_docdir}/%{name}/LICENSE.txt
%{_docdir}/%{name}/CHANGELOG.txt
%{_libdir}/%{name}

%files doc
%{_docdir}/%{name}/LICENSE.txt
%{_docdir}/%{name}

%changelog
* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Dec 02 2015 Clément David <c.david86@gmail.com> - 2.3.2-1
- update version

* Mon Nov 09 2015 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 2.2.4-5
- Add aarch64, ppc64, ppc64le, s390x support (from Debian/Ubuntu).

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Nov 28 2014 Clément David <c.david86@gmail.com> - 2.2.4-3
- Remove javadoc build as it timeout the ARM builders

* Wed Nov 19 2014 Clément David <c.david86@gmail.com> - 2.2.4-2
- Build for arm

* Thu Oct 16 2014 Clément David <c.david86@gmail.com> - 2.2.4-1
- Update version
- Add the Xcursor dependency

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jun 19 2014 Yaakov Selkowitz <yselkowi@redhat.com> - 2.0.2-4
- Fix FTBFS due to xmvn changes (#1106962)

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Jan 08 2014 Clément David <c.david86@gmail.com> - 2.0.2-2
- Fix bug #1001248 about docdir issue
- Allow the user to install javadoc without the main package

* Mon Sep 09 2013 Clément David <c.david86@gmail.com> - 2.0.2-1
- Update to the stable 2.0.2 version

* Tue Aug 13 2013 Clément David <c.david86@gmail.com> - 2.0-0.11.rc12
- Force the SDK root to / to pass the ARM build

* Thu Jul 11 2013 Clément David <c.david86@gmail.com> - 2.0-0.10.rc12
- Update version to rc12

* Mon May 06 2013 Clément David <c.david86@gmail.com> - 2.0-0.9.rc11
- Remove another debug message

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 2.0-0.8.rc11
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Mon Jan 21 2013 Clément David <c.david86@gmail.com> - 2.0-0.7.rc11
- Upgrade to the Java packaging draft (JNI jar/so location)
- Avoid using build-classpath to ease branch merge (and jnidir changes)

* Fri Jan 04 2013 Clément David <c.david86@gmail.com> - 2.0-0.6.rc11
- Update version

* Wed Dec 19 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 2.0-0.5.rc10
- revbump after jnidir change

* Fri Oct 05 2012 Clément David <c.david86@gmail.com> - 2.0-0.4.rc10
- Add p7zip dependency (to extract source)
- Fix fedora-review issues

* Tue Oct 02 2012 Clément David <c.david86@gmail.com> - 2.0-0.3.rc10
- Provide a pom file

* Thu Sep 20 2012 Clément David <c.david86@gmail.com> - 2.0-0.2.rc10
- Add javadoc full subpackage
- Provide symlink on %%{jnidir}

* Mon Sep 10 2012 Clément David <c.david86@gmail.com> - 2.0-0.1.rc10
- Initial package with inspiration on jogl spec

