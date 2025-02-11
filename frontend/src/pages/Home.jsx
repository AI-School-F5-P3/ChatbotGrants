import React, { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";

import "../app.css";
import { Logo } from "../components/Logo.jsx";
import classNames from "classnames";

import {
  Button,
  Card,
  Typography,
  Dialog,
  DialogHeader,
  DialogBody,
  DialogFooter,
  Input,
} from "@material-tailwind/react";

function Home() {
  const [open, setOpen] = React.useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm();
  const navigate = useNavigate();

  useEffect(() => {
    reset(); // Resetear el formulario al montar el componente
  }, [reset]);

  const onSubmit = async (data) => {
    const { email, password } = data;

    if (email && password) {
      // Login de prueba
      if (email === "admin@ayming.com" && password === "admin") {
        navigate("/chatbot"); // Redirige al chatbot
      }
      else {
        setOpen(true);
      }
    }
  };

  const handleClose = () => {
    setOpen(false);
  };

  const classEmail = classNames("placeholder:text-custom50Blue input-field", {
    error: errors.email,
  });

  const txtEmail = classNames("input-field", {
    error: errors.email,
  });

  const classPassword = classNames("placeholder:text-custom50Blue input-field", {
    error: errors.password,
  });

  return (
    <>
      <div className="flex items-center justify-center h-[calc(100vh-2rem)] text-white font-lato">
        <Card color="transparent" shadow={false} className="border border-custom50Blue p-16 pb-[6rem] rounded-lg">
          <Typography
            variant="h4"
            color="white"
            className="flex items-center justify-center"
          >
            <Logo variant="white" />
          </Typography>
          <form
            onSubmit={handleSubmit(onSubmit)}
            noValidate
            className="mt-8 mb-2 w-80 max-w-screen-lg sm:w-96"
          >
            <div className="mb-1 flex flex-col gap-6">
              <Input
                variant="standard"
                color="white"
                size="lg"
                placeholder="name@mail.com"
                className={classEmail}
                containerProps={{
                  className: "mt-2",
                }}
                label={`${errors.email ? "" : ""} Usuario`}
                {...register("email", {
                  required: "* Obligatorio",
                  pattern: {
                    value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                    message: "* Email inválido",
                  },
                })}
                // value="admin@ayming.com"
              />
              {/* Mensaje de error para el email */}
              {errors.email && (
                <p className="text-custom50Blue -mt-6 text-xs p-1 text-right">
                  {errors.email.message}
                </p>
              )}
              <Input
                variant="standard"
                color="white"
                type="password"
                size="lg"
                placeholder="********"
                className={classPassword}
                containerProps={{
                  className: "mt-2",
                }}
                label={`${errors.password ? "" : ""} Contraseña`}
                labelProps={{
                  className: "text-white",
                }}
                {...register("password", { required: "* Obligatorio" })}
              />
              {/* Mensaje de error para la contraseña */}
              {errors.password && (
                <p className="text-custom50Blue -mt-6 text-xs p-1 text-right">
                  {errors.password.message}
                </p>
              )}
            </div>

            <Button
              type="submit"
              className="mt-20 rounded-full h-12 bg-white text-customLightBlue text-base "
              fullWidth
            >
              Entrar
            </Button>
          </form>
          <Dialog open={open} handler={handleClose}>
            <DialogBody className="grid place-items-center gap-4">
              
              <Typography className="text-customBlue mt-8" variant="h4">
                Ups!
              </Typography>
              <Typography className="text-center font-normal">
                Usuario o contraseña incorrectos
              </Typography>
              <Button color="white" className="mt-10 px-10 rounded-full h-12 text-base text-white bg-customLightBlue" onClick={handleClose}>
                Cerrar
              </Button>
            </DialogBody>
          </Dialog>
        </Card>
      </div>
    </>
  );
}

export default Home;
